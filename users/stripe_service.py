import stripe
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    """Service class for handling Stripe operations"""
    
    @staticmethod
    def create_customer(user):
        """Create a Stripe customer for the user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip(),
                metadata={'user_id': user.id}
            )
            user.stripe_customer_id = customer.id
            user.save()
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {e}")
            raise
    
    @staticmethod
    def get_or_create_customer(user):
        """Get existing customer or create a new one"""
        if user.stripe_customer_id:
            try:
                return stripe.Customer.retrieve(user.stripe_customer_id)
            except stripe.error.InvalidRequestError:
                # Customer doesn't exist, create new one
                pass
        
        return StripeService.create_customer(user)
    
    @staticmethod
    def create_checkout_session(user, plan, success_url, cancel_url):
        """Create a Stripe checkout session for subscription"""
        try:
            customer = StripeService.get_or_create_customer(user)
            
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': user.id,
                    'plan_id': plan.id,
                }
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription_id):
        """Cancel a Stripe subscription"""
        try:
            return stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {e}")
            raise
    
    @staticmethod
    def reactivate_subscription(subscription_id):
        """Reactivate a canceled subscription"""
        try:
            return stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error reactivating subscription: {e}")
            raise
    
    @staticmethod
    def handle_successful_payment(session):
        """Handle successful payment from webhook"""
        from .models import User, Plan
        
        try:
            user_id = session.metadata.get('user_id')
            plan_id = session.metadata.get('plan_id')
            
            if not user_id or not plan_id:
                logger.error("Missing user_id or plan_id in session metadata")
                return False
            
            user = User.objects.get(id=user_id)
            plan = Plan.objects.get(id=plan_id)
            
            # Get the subscription from Stripe
            subscription = stripe.Subscription.retrieve(session.subscription)
            
            # Update user subscription
            user.current_plan = plan
            user.subscription_status = 'active'
            user.stripe_subscription_id = subscription.id
            user.subscription_started_at = timezone.now()
            user.subscription_expires_at = timezone.datetime.fromtimestamp(
                subscription.current_period_end, tz=timezone.utc
            )
            user.save()
            
            logger.info(f"User {user.email} successfully subscribed to {plan.name}")
            return True
            
        except (User.DoesNotExist, Plan.DoesNotExist) as e:
            logger.error(f"Error handling successful payment: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error handling successful payment: {e}")
            return False
    
    @staticmethod
    def handle_subscription_updated(subscription):
        """Handle subscription update from webhook"""
        from .models import User
        
        try:
            user = User.objects.get(stripe_subscription_id=subscription.id)
            
            # Update subscription status
            status_mapping = {
                'active': 'active',
                'canceled': 'canceled',
                'incomplete': 'inactive',
                'incomplete_expired': 'inactive',
                'past_due': 'past_due',
                'trialing': 'trialing',
                'unpaid': 'inactive',
            }
            
            user.subscription_status = status_mapping.get(subscription.status, 'inactive')
            user.subscription_expires_at = timezone.datetime.fromtimestamp(
                subscription.current_period_end, tz=timezone.utc
            )
            user.save()
            
            logger.info(f"Updated subscription for user {user.email}: {subscription.status}")
            return True
            
        except User.DoesNotExist:
            logger.error(f"User not found for subscription {subscription.id}")
            return False
        except Exception as e:
            logger.error(f"Error handling subscription update: {e}")
            return False
    
    @staticmethod
    def handle_subscription_deleted(subscription):
        """Handle subscription deletion from webhook"""
        from .models import User
        
        try:
            user = User.objects.get(stripe_subscription_id=subscription.id)
            user.subscription_status = 'canceled'
            user.save()
            
            logger.info(f"Subscription deleted for user {user.email}")
            return True
            
        except User.DoesNotExist:
            logger.error(f"User not found for deleted subscription {subscription.id}")
            return False
        except Exception as e:
            logger.error(f"Error handling subscription deletion: {e}")
            return False 