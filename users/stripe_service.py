import logging
from datetime import datetime, timedelta

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Plan

logger = logging.getLogger(__name__)
User = get_user_model()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service class for handling Stripe operations"""

    @staticmethod
    def create_customer(email=None, name=None, user=None, **kwargs):
        """Create a Stripe customer"""
        try:
            customer_data = {}

            if user:
                customer_data.update(
                    {
                        "email": user.email,
                        "name": f"{user.first_name} {user.last_name}".strip(),
                        "metadata": {"user_id": user.id},
                    }
                )
            else:
                if email is None or email == "":
                    raise ValueError("Email is required and cannot be None or empty")
                customer_data["email"] = email
                if name:
                    customer_data["name"] = name

            # Add any additional kwargs
            customer_data.update(kwargs)

            customer = stripe.Customer.create(**customer_data)

            if user:
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

        return StripeService.create_customer(user=user)

    @staticmethod
    def create_checkout_session(
        user=None,
        plan=None,
        success_url=None,
        cancel_url=None,
        customer_id=None,
        **kwargs,
    ):
        """Create a Stripe checkout session for subscription"""
        try:
            if customer_id:
                customer_id_to_use = customer_id
            elif user:
                customer = StripeService.get_or_create_customer(user)
                customer_id_to_use = customer.id
            else:
                raise ValueError("Either user or customer_id must be provided")

            # Get mode from kwargs or default to subscription
            mode = kwargs.pop("mode", "subscription")

            session_data = {
                "customer": customer_id_to_use,
                "payment_method_types": ["card"],
                "mode": mode,
                "success_url": success_url,
                "cancel_url": cancel_url,
            }

            if plan and hasattr(plan, "stripe_price_id"):
                session_data["line_items"] = [
                    {
                        "price": plan.stripe_price_id,
                        "quantity": 1,
                    }
                ]
                session_data["metadata"] = {
                    "user_id": user.id if user else "",
                    "plan_id": plan.id,
                }
            elif "price_id" in kwargs:
                # Handle direct price_id parameter
                price_id = kwargs.pop("price_id")
                session_data["line_items"] = [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ]

            # Add any additional kwargs
            session_data.update(kwargs)

            session = stripe.checkout.Session.create(**session_data)
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise

    @staticmethod
    def get_checkout_session(session_id):
        """Get a Stripe checkout session by ID"""
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving checkout session: {e}")
            raise

    @staticmethod
    def create_subscription(customer_id, price_id, **kwargs):
        """Create a Stripe subscription"""
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
            }
            subscription_data.update(kwargs)

            return stripe.Subscription.create(**subscription_data)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {e}")
            raise

    @staticmethod
    def get_subscription(subscription_id):
        """Get a Stripe subscription"""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving subscription: {e}")
            raise

    @staticmethod
    def update_subscription(subscription_id, **kwargs):
        """Update a Stripe subscription"""
        try:
            return stripe.Subscription.modify(subscription_id, **kwargs)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating subscription: {e}")
            raise

    @staticmethod
    def cancel_subscription(subscription_id):
        """Cancel a Stripe subscription immediately"""
        try:
            return stripe.Subscription.cancel(subscription_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {e}")
            raise

    @staticmethod
    def cancel_subscription_at_period_end(subscription_id):
        """Cancel a Stripe subscription at period end"""
        try:
            return stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=True
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription at period end: {e}")
            raise

    @staticmethod
    def reactivate_subscription(subscription_id):
        """Reactivate a canceled subscription"""
        try:
            return stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=False
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error reactivating subscription: {e}")
            raise

    @staticmethod
    def retrieve_event(event_id):
        """Retrieve a Stripe event"""
        try:
            return stripe.Event.retrieve(event_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving event: {e}")
            raise

    @staticmethod
    def process_webhook_event(event):
        """Process a webhook event"""
        try:
            event_type = event.get("type", "")

            if event_type == "checkout.session.completed":
                session = event.get("data", {}).get("object", {})
                if session.get("payment_status") == "paid":
                    return StripeService.handle_successful_payment(session)
            elif event_type == "customer.subscription.updated":
                subscription = event.get("data", {}).get("object", {})
                return StripeService.handle_subscription_updated(subscription)
            elif event_type == "customer.subscription.deleted":
                subscription = event.get("data", {}).get("object", {})
                return StripeService.handle_subscription_deleted(subscription)

            # For unknown event types, return None (ignored)
            return None

        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            return False

    @staticmethod
    def handle_successful_payment(session):
        try:
            user_id = session.get("metadata", {}).get("user_id")
            subscription_id = session.get("subscription")
            if not user_id or not subscription_id:
                logger.error("Missing user_id or subscription_id in session metadata")
                return False
            user = User.objects.get(id=user_id)
            user.stripe_subscription_id = subscription_id
            user.save()
            logger.info(f"Linked subscription_id {subscription_id} to user {user.email}")
            return True
        except User.DoesNotExist:
            logger.error(f"User not found for user_id {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error linking subscription_id to user: {e}")
            return False

    @staticmethod
    def handle_subscription_updated(subscription):
        """Handle subscription update from webhook"""
        from .models import User

        try:
            subscription_id = (
                subscription.get("id")
                if isinstance(subscription, dict)
                else subscription.id
            )
            user = User.objects.get(stripe_subscription_id=subscription_id)

            # Update subscription status
            status_mapping = {
                "active": "active",
                "canceled": "canceled",
                "incomplete": "inactive",
                "incomplete_expired": "inactive",
                "past_due": "past_due",
                "trialing": "trialing",
                "unpaid": "inactive",
            }

            subscription_status = (
                subscription.get("status")
                if isinstance(subscription, dict)
                else subscription.status
            )
            current_period_end = (
                subscription.get("current_period_end")
                if isinstance(subscription, dict)
                else subscription.current_period_end
            )
            current_period_start = (
                subscription.get("current_period_start")
                if isinstance(subscription, dict)
                else subscription.current_period_start
            )

            user.subscription_status = status_mapping.get(
                subscription_status, "inactive"
            )
            if current_period_end:
                user.subscription_expires_at = timezone.make_aware(
                    datetime.fromtimestamp(current_period_end)
                )
                user.current_period_end = timezone.make_aware(
                    datetime.fromtimestamp(current_period_end)
                )
            if current_period_start:
                user.current_period_start = timezone.make_aware(
                    datetime.fromtimestamp(current_period_start)
                )
            user.save()

            logger.info(
                f"Updated subscription for user {user.email}: {subscription_status}"
            )
            return True

        except User.DoesNotExist:
            logger.error(f"User not found for subscription {subscription_id}")
            return False
        except Exception as e:
            logger.error(f"Error handling subscription update: {e}")
            return False

    @staticmethod
    def handle_subscription_deleted(subscription):
        """Handle subscription deletion from webhook"""
        from .models import User

        try:
            subscription_id = (
                subscription.get("id")
                if isinstance(subscription, dict)
                else subscription.id
            )
            user = User.objects.get(stripe_subscription_id=subscription_id)
            user.subscription_status = "canceled"
            user.save()

            logger.info(f"Subscription deleted for user {user.email}")
            return True

        except User.DoesNotExist:
            logger.error(f"User not found for deleted subscription {subscription_id}")
            return False
        except Exception as e:
            logger.error(f"Error handling subscription deletion: {e}")
            return False

    @staticmethod
    def get_customer(customer_id):
        """Get a Stripe customer by ID"""
        try:
            return stripe.Customer.retrieve(customer_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving customer: {e}")
            raise

    @staticmethod
    def update_customer(customer_id, **kwargs):
        """Update a Stripe customer"""
        try:
            return stripe.Customer.modify(customer_id, **kwargs)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating customer: {e}")
            raise

    @staticmethod
    def delete_customer(customer_id):
        """Delete a Stripe customer"""
        try:
            return stripe.Customer.delete(customer_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error deleting customer: {e}")
            raise
