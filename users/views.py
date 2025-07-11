import json
import logging
from datetime import datetime, timedelta

import stripe
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from rest_framework import generics, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from decouple import config

from .forms import WaitingListForm
from .models import Plan, TokenHistory, User, PaymentFailure
from .serializers import (
    PlanSerializer,
    TokenHistorySerializer,
    TokenRegenerationSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .stripe_service import StripeService
from .middleware import set_payment_failure_flags, clear_payment_failure_flags

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


def get_permission_classes():
    if settings.DEBUG and not getattr(settings, 'TESTING', False):
        logger.info("DEBUG mode is on. Allowing all requests.")
        return [permissions.AllowAny]
    return [permissions.IsAuthenticated]


permissions_ = get_permission_classes()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]  # Always allow registration
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.data["message"] = "User registered successfully"
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = permissions_
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class RegenerateRequestTokenView(APIView):
    permission_classes = permissions_
    serializer_class = TokenRegenerationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if "auto_renew" in serializer.validated_data:
            user.token_auto_renew = serializer.validated_data["auto_renew"]
        if "validity_days" in serializer.validated_data:
            user.token_validity_days = serializer.validated_data["validity_days"]

        save_old = serializer.validated_data.get("save_old", True)
        user.generate_new_request_token(save_old=save_old)

        token_info = user.get_token_info()
        response_data = {
            "new_token": str(user.request_token),
            "message": "Token regenerated successfully",
            "token_info": token_info,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class TokenHistoryView(APIView):
    permission_classes = permissions_

    def get(self, request):
        user = request.user

        token_history = user.token_history.all()
        serializer = TokenHistorySerializer(token_history, many=True)

        response_data = {
            "results": serializer.data,
            "current_token": user.get_token_info(),
            "previous_tokens": user.previous_tokens,
        }

        return Response(response_data, status=status.HTTP_200_OK)


def home(request):
    return render(request, "home.html")


@login_required
def profile(request):
    _token_history = TokenHistory.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    token_info = request.user.get_token_info()
    token_info["is_active"] = not request.user.is_token_expired()

    # Calculate usage percentage for progress bar
    daily_requests_made = request.user.daily_requests_made
    daily_request_limit = request.user.daily_request_limit
    usage_percentage = 0
    if daily_request_limit > 0:
        usage_percentage = (daily_requests_made / daily_request_limit) * 100
        # Cap at 100% to avoid overflow in UI
        usage_percentage = min(usage_percentage, 100)

    # Create a complete token history including the current token
    all_tokens = []

    # Add current token as the first item
    current_token = {
        "token": str(request.user.request_token),
        "created_at": request.user.request_token_created,
        "expires_at": request.user.request_token_expires,
        "never_expires": request.user.token_never_expires,
        "is_active": not request.user.is_token_expired(),
        "is_current": True,
        "status_display": "Current Token",
    }
    all_tokens.append(current_token)

    # Add historical tokens
    for token in _token_history:
        token_data = {
            "token": token.token,
            "created_at": token.created_at,
            "expires_at": token.expires_at,
            "never_expires": token.never_expires,
            "is_active": token.is_active,
            "is_current": False,
            "status_display": token.status_display,
        }
        all_tokens.append(token_data)

    context = {
        "token_info": token_info,
        "token_history": _token_history,
        "all_tokens": all_tokens,  # Complete token list including current
        "user": request.user,
        "daily_usage": {
            "made": daily_requests_made,
            "limit": daily_request_limit,
            "remaining": max(0, daily_request_limit - daily_requests_made),
            "percentage": round(usage_percentage, 1),  # Round to 1 decimal place
        },
    }
    return render(request, "profile.html", context)


@login_required
@require_http_methods(["POST"])
def regenerate_token(request):
    try:
        never_expires = request.POST.get("never_expires") == "true"
        request.user.generate_new_request_token(
            save_old=True, never_expires=never_expires
        )
        messages.success(request, "New token generated successfully.")
    except Exception as e:
        messages.error(request, f"Failed to generate new token: {str(e)}")

    return redirect("profile")


@api_view(["GET", "POST"])
@permission_classes([permissions.AllowAny])
def register_user(request):
    return redirect("waiting_list")


def waiting_list(request):
    """Handle waiting list registration form"""
    if request.method == "POST":
        form = WaitingListForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    "Thank you for your interest! You've been added to our waiting list. "
                    "We'll notify you as soon as the API becomes available.",
                )
                return redirect("waiting_list_success")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                    messages.info(
                        request,
                        "This email is already on our waiting list. "
                        "We'll notify you when the API becomes available!",
                    )
                else:
                    messages.error(
                        request,
                        "There was an issue adding you to the waiting list. Please try again.",
                    )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = WaitingListForm()

    return render(request, "waiting_list.html", {"form": form})


def waiting_list_success(request):
    """Success page after joining waiting list"""
    return render(request, "waiting_list_success.html")


@api_view(["GET", "PATCH"])
@permission_classes(permissions_)
def user_profile(request):
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes(permissions_)
def regenerate_request_token(request):
    try:
        save_old = request.data.get("save_old", True)
        auto_renew = request.data.get("auto_renew", request.user.auto_renew_token)
        validity_days = request.data.get(
            "validity_days", request.user.token_validity_days
        )

        request.user.regenerate_request_token(
            save_old=save_old, auto_renew=auto_renew, validity_days=validity_days
        )

        return Response(
            {
                "request_token": request.user.request_token,
                "created": request.user.token_created_at,
                "expires": request.user.token_expires_at,
                "auto_renew": request.user.auto_renew_token,
                "validity_days": request.user.token_validity_days,
            }
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes(permissions_)
def token_history(request):
    history = TokenHistory.objects.filter(user=request.user).order_by("-created_at")[:5]
    serializer = TokenHistorySerializer(history, many=True)

    response_data = {
        "results": serializer.data,
        "current_token": request.user.get_token_info(),
        "previous_tokens": request.user.previous_tokens,
    }

    return Response(response_data, status=status.HTTP_200_OK)


class PlansListView(generics.ListAPIView):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class AsaasCheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def post(self, request):
        logger.info(f"AsaasCheckoutView called by user: {request.user}")
        logger.info(f"User authenticated: {request.user.is_authenticated}")
        logger.info(f"Request data: {request.data}")
        PLAN_PRICES = {
            'basic': 29.00,
            'pro': 57.00,
            'premium': 148.00,
        }
        plan_id = request.data.get('plan_id')
        if plan_id not in PLAN_PRICES:
            return Response({'error': 'Invalid plan_id'}, status=400)
        price = PLAN_PRICES[plan_id]
        user = request.user
        # Asaas Sandbox API Key
        ASAAS_API_KEY = config("ASAAS_API_KEY", default="")
        if not ASAAS_API_KEY:
            return Response({'error': 'ASAAS_API_KEY not configured'}, status=500)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'access_token': ASAAS_API_KEY,
        }
        # 1. Create customer (temporary) test
        customer_payload = {
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'cpfCnpj': '00000000000',  # Optional: can be adjusted
        }
        customer_resp = requests.post(
            'https://sandbox.asaas.com/api/v3/customers',
            headers=headers,
            json=customer_payload
        )
        if customer_resp.status_code not in (200, 201):
            return Response({'error': 'Failed to create customer', 'asaas': customer_resp.json()}, status=400)
        customer_id = customer_resp.json().get('id')
        if not customer_id:
            return Response({'error': 'No customer id returned from Asaas'}, status=400)
        # 2. Create payment (temporary) test
        payment_payload = {
            'customer': customer_id,
            'billingType': 'PIX',
            'value': price,
            'dueDate': '2025-07-15',
            'description': f'Plano {plan_id.capitalize()} - Financial Data API',
        }
        payment_resp = requests.post(
            'https://sandbox.asaas.com/api/v3/payments',
            headers=headers,
            json=payment_payload
        )
        if payment_resp.status_code not in (200, 201):
            return Response({'error': 'Failed to create payment', 'asaas': payment_resp.json()}, status=400)
        payment_data = payment_resp.json()
        invoice_url = payment_data.get('invoiceUrl') or payment_data.get('bankSlipUrl')
        if not invoice_url:
            return Response({'error': 'No invoice url returned from Asaas', 'asaas': payment_data}, status=400)
        return Response({'invoice_url': invoice_url})


@login_required
@require_POST
def create_checkout_session(request):
    try:
        is_api_request = request.content_type == "application/json"

        if is_api_request:
            import json

            data = json.loads(request.body)
            plan_id = data.get("plan_id")
        else:
            plan_id = request.POST.get("plan_id")

        plan = get_object_or_404(Plan, id=plan_id, is_active=True)

        if plan.is_free:
            request.user.upgrade_to_plan(plan)
            if is_api_request:
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Successfully upgraded to {plan.name} plan!",
                    }
                )
            else:
                messages.success(request, f"Successfully upgraded to {plan.name} plan!")
                return redirect("profile")

        if not plan.stripe_price_id:
            if is_api_request:
                return JsonResponse(
                    {"error": "This plan is not available for purchase."}, status=400
                )
            else:
                messages.error(request, "This plan is not available for purchase.")
                return redirect("home")

        success_url = request.build_absolute_uri(reverse("subscription_success"))
        cancel_url = request.build_absolute_uri(reverse("plans"))

        session = StripeService.create_checkout_session(
            user=request.user, plan=plan, success_url=success_url, cancel_url=cancel_url
        )

        if is_api_request:
            return JsonResponse({"checkout_url": session.url, "session_id": session.id})
        else:
            return redirect(session.url, code=303)

    except stripe.error.APIConnectionError as e:
        if is_api_request:
            return JsonResponse(
                {"error": "Service temporarily unavailable. Please try again later."},
                status=503,
            )
        else:
            messages.error(
                request, "Service temporarily unavailable. Please try again later."
            )
            return redirect("plans")
    except stripe.error.AuthenticationError as e:
        if is_api_request:
            return JsonResponse(
                {"error": "Authentication error with payment service."}, status=500
            )
        else:
            messages.error(request, "Payment service error. Please try again later.")
            return redirect("plans")
    except stripe.error.StripeError as e:
        if is_api_request:
            return JsonResponse(
                {"error": f"Payment service error: {str(e)}"}, status=400
            )
        else:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect("pricing")
    except Http404:
        raise
    except Exception as e:
        if is_api_request:
            return JsonResponse({"error": str(e)}, status=400)
        else:
            messages.error(request, f"Error creating checkout session: {str(e)}")
            return redirect("pricing")


@login_required
def subscription_success(request):
    return render(request, "subscription_success.html")


@login_required
@require_POST
def cancel_subscription(request):
    try:
        if not request.user.stripe_subscription_id:
            messages.error(request, "No active subscription to cancel.")
            return redirect("profile")

        StripeService.cancel_subscription(request.user.stripe_subscription_id)
        request.user.cancel_subscription()

        messages.success(
            request, "Your subscription has been canceled and will not renew."
        )

    except Exception as e:
        messages.error(request, f"Error canceling subscription: {str(e)}")

    return redirect("profile")


@login_required
@require_POST
def reactivate_subscription(request):
    try:
        if not request.user.stripe_subscription_id:
            messages.error(request, "No subscription to reactivate.")
            return redirect("profile")

        StripeService.reactivate_subscription(request.user.stripe_subscription_id)

        if request.user.reactivate_subscription():
            messages.success(request, "Your subscription has been reactivated!")
        else:
            messages.error(request, "Unable to reactivate subscription.")

    except Exception as e:
        messages.error(request, f"Error reactivating subscription: {str(e)}")

    return redirect("profile")


@csrf_exempt
def stripe_webhook(request):
    logger.info("=== Stripe webhook called ===")
    if request.method != "POST":
        logger.info("Invalid method, returning 405")
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    if request.content_type != "application/json":
        logger.info("Invalid content type, returning 400")
        return JsonResponse(
            {"error": "Content-Type must be application/json"}, status=400
        )

    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
    logger.info(f"Webhook secret configured: {bool(webhook_secret)}")
    if not webhook_secret:
        logger.error("Webhook secret not configured")
        return JsonResponse({"error": "Webhook secret not configured"}, status=400)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    logger.info(f"Signature header present: {bool(sig_header)}")

    try:
        logger.info("Verifying Stripe signature...")
        stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        logger.info("Signature verification successful")
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Signature verification failed: {e}")
        return JsonResponse({"error": "Invalid signature"}, status=400)

    try:
        event = json.loads(payload)

        # Enhanced webhook event handling
        handlers = {
            'customer.subscription.created': handle_subscription_created,
            'customer.subscription.updated': handle_subscription_updated,
            'customer.subscription.deleted': handle_subscription_canceled,
            'invoice.payment_failed': handle_payment_failed,
            'invoice.payment_succeeded': handle_payment_succeeded,
            'customer.subscription.trial_will_end': handle_trial_ending,
            'invoice.payment_action_required': handle_payment_action_required,
        }
        
        handler = handlers.get(event['type'])
        logger.info(f"Processing webhook event type: {event['type']}")
        if handler:
            try:
                logger.info(f"Calling handler for {event['type']}")
                logger.info(f"Event data: {event['data']['object']}")
                result = handler(event['data']['object'])
                logger.info(f"Handler result: {result}")
                return JsonResponse({"status": "success", "processed": True, "result": result})
            except Exception as e:
                logger.error(f"Webhook handler error for {event['type']}: {e}")
                return JsonResponse({"status": "error", "message": str(e)}, status=500)
        else:
            logger.info(f"Unhandled webhook event type: {event['type']}")
            return JsonResponse({"status": "success", "processed": False})

    except Exception as e:
        logger.error(f"Unexpected error in webhook: {e}")
        return JsonResponse({"status": "error"}, status=500)


def handle_subscription_created(subscription_data):
    """Handle new subscription creation"""
    try:
        from .models import Plan
        
        customer_id = subscription_data['customer']
        user = User.objects.get(stripe_customer_id=customer_id)
        
        # Update user subscription info
        user.stripe_subscription_id = subscription_data['id']
        user.subscription_status = subscription_data['status']
        from datetime import datetime as dt, timezone as tz
        user.current_period_start = dt.fromtimestamp(
            subscription_data['current_period_start'], tz=tz.utc
        )
        user.current_period_end = dt.fromtimestamp(
            subscription_data['current_period_end'], tz=tz.utc
        )
        user.subscription_expires_at = user.current_period_end
        
        # Update plan based on price ID
        if subscription_data['items']['data']:
            price_id = subscription_data['items']['data'][0]['price']['id']
            try:
                plan = Plan.objects.get(stripe_price_id=price_id)
                user.current_plan = plan
            except Plan.DoesNotExist:
                logger.warning(f"Plan not found for price ID: {price_id}")
        
        # Clear any payment restrictions
        clear_payment_failure_flags(user)
        user.save()
        
        logger.info(f"Subscription created for user {user.id}: {subscription_data['id']}")
        return {"user_id": user.id, "subscription_id": subscription_data['id']}
        
    except User.DoesNotExist:
        logger.error(f"User not found for customer ID: {customer_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling subscription creation: {e}")
        return {"error": str(e)}


def handle_subscription_updated(subscription_data):
    """Handle subscription updates with enhanced rate limiting integration"""
    try:
        from .models import Plan
        from django.core.cache import caches
        
        subscription_id = subscription_data['id']
        logger.info(f"Processing subscription update for ID: {subscription_id}")
        user = User.objects.get(stripe_subscription_id=subscription_id)
        logger.info(f"Found user {user.id} with subscription {subscription_id}")
        
        # Update status and dates
        old_status = user.subscription_status
        new_status = subscription_data['status']
        logger.info(f"Status change: {old_status} -> {new_status}")
        user.subscription_status = new_status
        from datetime import datetime as dt, timezone as tz
        user.current_period_start = dt.fromtimestamp(
            subscription_data['current_period_start'], tz=tz.utc
        )
        user.current_period_end = dt.fromtimestamp(
            subscription_data['current_period_end'], tz=tz.utc
        )
        user.subscription_expires_at = user.current_period_end
        
        # Handle plan changes
        if subscription_data['items']['data']:
            price_id = subscription_data['items']['data'][0]['price']['id']
            try:
                new_plan = Plan.objects.get(stripe_price_id=price_id)
                if user.current_plan != new_plan:
                    logger.info(f"Plan changed for user {user.id}: {user.current_plan} -> {new_plan}")
                    user.current_plan = new_plan
                    # Clear cached limits to force refresh
                    user.limits_cache_updated = None
            except Plan.DoesNotExist:
                logger.error(f"Plan not found for price ID: {price_id}")
        
        # Handle status-specific actions
        if subscription_data['status'] == 'active':
            clear_payment_failure_flags(user)
            if old_status in ['past_due', 'incomplete']:
                logger.info(f"Subscription reactivated for user {user.id}")
        elif subscription_data['status'] in ['past_due', 'incomplete']:
            set_payment_failure_flags(user, 'limited')
            logger.warning(f"Subscription payment issues for user {user.id}")
        elif subscription_data['status'] == 'canceled':
            logger.info(f"Subscription canceled for user {user.id}")
        
        user.save()
        logger.info(f"User {user.id} saved with new status: {user.subscription_status}")
        
        # Clear rate limiting cache
        cache = caches['rate_limit']
        cache_key = f"user_limits:{user.id}"
        cache.delete(cache_key)
        
        logger.info(f"Subscription update completed for user {user.id}")
        return {"user_id": user.id, "status": subscription_data['status']}
        
    except User.DoesNotExist:
        logger.error(f"User not found for subscription ID: {subscription_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling subscription update: {e}")
        return {"error": str(e)}


def handle_subscription_canceled(subscription_data):
    """Handle subscription cancellation"""
    try:
        subscription_id = subscription_data['id']
        user = User.objects.get(stripe_subscription_id=subscription_id)
        
        user.cancel_subscription()
        clear_payment_failure_flags(user)  # Clear restrictions but subscription is still canceled
        
        logger.info(f"Subscription canceled for user {user.id}")
        return {"user_id": user.id, "canceled": True}
        
    except User.DoesNotExist:
        logger.error(f"User not found for canceled subscription: {subscription_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {e}")
        return {"error": str(e)}


def handle_payment_failed(invoice_data):
    """Handle payment failures with progressive restrictions"""
    try:
        subscription_id = invoice_data.get('subscription')
        if not subscription_id:
            return {"error": "No subscription ID in invoice"}
        
        user = User.objects.get(stripe_subscription_id=subscription_id)
        
        # Check number of recent payment failures
        recent_failures = PaymentFailure.objects.filter(
            user=user,
            failed_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Apply progressive restrictions
        if recent_failures == 0:
            restriction_level = 'warning'
        elif recent_failures == 1:
            restriction_level = 'limited'
        else:
            restriction_level = 'suspended'
        
        set_payment_failure_flags(user, restriction_level)
        
        logger.warning(f"Payment failed for user {user.id}, restriction level: {restriction_level}")
        return {"user_id": user.id, "restriction_level": restriction_level}
        
    except User.DoesNotExist:
        logger.error(f"User not found for failed payment, subscription: {subscription_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling payment failure: {e}")
        return {"error": str(e)}


def handle_payment_succeeded(invoice_data):
    """Handle successful payments"""
    try:
        subscription_id = invoice_data.get('subscription')
        if not subscription_id:
            return {"success": True, "message": "No subscription to update"}
        
        user = User.objects.get(stripe_subscription_id=subscription_id)
        
        # Clear payment failure restrictions
        clear_payment_failure_flags(user)
        
        # If subscription was in a problematic state, reactivate it
        if user.subscription_status in ['past_due', 'incomplete']:
            user.subscription_status = 'active'
            user.save()
        
        logger.info(f"Payment succeeded for user {user.id}")
        return {"user_id": user.id, "payment_cleared": True}
        
    except User.DoesNotExist:
        logger.error(f"User not found for successful payment, subscription: {subscription_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling payment success: {e}")
        return {"error": str(e)}


def handle_trial_ending(subscription_data):
    """Handle trial ending notification"""
    try:
        subscription_id = subscription_data['id']
        user = User.objects.get(stripe_subscription_id=subscription_id)
        
        # Log trial ending for monitoring
        logger.info(f"Trial ending for user {user.id}, subscription: {subscription_id}")
        
        # Could send notification email here
        return {"user_id": user.id, "trial_ending": True}
        
    except User.DoesNotExist:
        logger.error(f"User not found for trial ending, subscription: {subscription_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling trial ending: {e}")
        return {"error": str(e)}


def handle_payment_action_required(invoice_data):
    """Handle when payment requires customer action"""
    try:
        subscription_id = invoice_data.get('subscription')
        if not subscription_id:
            return {"message": "No subscription to update"}
        
        user = User.objects.get(stripe_subscription_id=subscription_id)
        
        # Apply limited restrictions but not as severe as failed payment
        set_payment_failure_flags(user, 'warning')
        
        logger.info(f"Payment action required for user {user.id}")
        return {"user_id": user.id, "action_required": True}
        
    except User.DoesNotExist:
        logger.error(f"User not found for payment action required, subscription: {subscription_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling payment action required: {e}")
        return {"error": str(e)}


@api_view(["GET"])
@permission_classes(permissions_)
def user_subscription(request):
    user = request.user
    data = {
        "current_plan": PlanSerializer(user.current_plan).data
        if user.current_plan
        else None,
        "subscription_status": user.subscription_status,
        "subscription_expires_at": user.subscription_expires_at,
        "subscription_days_remaining": user.subscription_days_remaining,
        "is_subscription_active": user.is_subscription_active,
        "daily_request_limit": user.daily_request_limit,
        "daily_requests_made": user.daily_requests_made,
        "requests_remaining": max(
            0, user.daily_request_limit - user.daily_requests_made
        ),
    }
    return Response(data)


@api_view(["POST"])
@permission_classes(permissions_)
def create_checkout_session_api(request):
    try:
        plan_id = request.data.get("plan_id")
        plan = get_object_or_404(Plan, id=plan_id, is_active=True)

        if plan.is_free:
            request.user.upgrade_to_plan(plan)
            return Response(
                {
                    "success": True,
                    "message": f"Successfully upgraded to {plan.name} plan!",
                }
            )

        if not plan.stripe_price_id:
            return Response(
                {"error": "This plan is not available for purchase."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_url = request.data.get(
            "success_url", request.build_absolute_uri(reverse("subscription-success"))
        )
        cancel_url = request.data.get(
            "cancel_url", request.build_absolute_uri(reverse("home"))
        )

        session = StripeService.create_checkout_session(
            user=request.user, plan=plan, success_url=success_url, cancel_url=cancel_url
        )

        return Response({"checkout_url": session.url, "session_id": session.id})

    except stripe.error.APIConnectionError as e:
        return Response(
            {"error": "Service temporarily unavailable. Please try again later."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except stripe.error.AuthenticationError as e:
        return Response(
            {"error": "Authentication error with payment service."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except stripe.error.StripeError as e:
        return Response(
            {"error": f"Payment service error: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def csrf_failure_view(request, reason=""):
    if request.content_type == "application/json":
        return JsonResponse(
            {
                "error": "CSRF verification failed",
                "reason": reason,
                "message": "Please refresh the page and try again.",
            },
            status=403,
        )
    else:
        return render(
            request,
            "csrf_failure.html",
            {
                "reason": reason,
                "message": "CSRF verification failed. Please refresh the page and try again.",
            },
            status=403,
        )


@login_required
@require_GET
def subscribe_asaas(request):
    plan = request.GET.get('plan')
    if not plan:
        return redirect('home')
    # Reuse the logic from AsaasCheckoutView
    class DummyRequest:
        def __init__(self, user, plan_id):
            self.user = user
            self.data = {'plan_id': plan_id}
    drf_request = DummyRequest(request.user, plan)
    view = AsaasCheckoutView()
    response = view.post(drf_request)
    data = response.data
    invoice_url = data.get('invoice_url')
    if invoice_url:
        return redirect(invoice_url)
    else:
        # In case of error, redirect to home with message
        return redirect('home')
