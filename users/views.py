import json
import logging
import re
from datetime import datetime as dt
from datetime import timezone as tz
from urllib.parse import urlparse

import requests
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache, caches
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Feature, SubscriptionStatus

from .forms import WaitingListForm
from .models import Plan, TokenHistory, User
from .serializers import (
    PlanSerializer,
    TokenHistorySerializer,
    TokenRegenerationSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .stripe_service import StripeService

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


def get_permission_classes():
    if settings.DEBUG:
        logger.debug("DEBUG mode is on. Allowing all requests.")
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
    plans = Plan.objects.filter(is_active=True).prefetch_related('features').order_by('price_monthly')
    all_features = Feature.objects.filter(is_active=True).order_by('name')

    return render(request, 'home.html', {'plans': plans, 'all_features': all_features})


@login_required
def profile(request):
    _token_history = TokenHistory.objects.filter(user=request.user).order_by("-created_at")

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
        # Adicionado para exibir planos disponíveis na troca de plano
        "plans": Plan.objects.filter(is_active=True).order_by("price_monthly"),
        "plan_id_map": {plan.name: plan.id for plan in Plan.objects.filter(is_active=True)},
        "current_plan": request.user.current_plan,
    }
    return render(request, "profile.html", context)


@login_required
@require_http_methods(["POST"])
def regenerate_token(request):
    try:
        never_expires = request.POST.get("never_expires") == "true"
        request.user.generate_new_request_token(save_old=True, never_expires=never_expires)
        messages.success(request, "New token generated successfully.")
    except Exception as e:
        messages.error(request, f"Failed to generate new token: {str(e)}")

    return redirect("profile")


def register_user(request):
    """Handle user registration for web interface"""
    if request.method == "POST":
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        errors = []
        
        if not email:
            errors.append("Email is required.")
        elif User.objects.filter(email=email).exists():
            errors.append("Email already exists.")
            
        if not password1:
            errors.append("Password is required.")
        elif len(password1) < 8:
            errors.append("Password must be at least 8 characters long.")
            
        if password1 != password2:
            errors.append("Passwords don't match.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                user = User.objects.create_user(
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                messages.success(
                    request,
                    "Registration successful! You can now log in to your account."
                )
                return redirect("login")
            except Exception as e:
                messages.error(
                    request,
                    "There was an issue creating your account. Please try again."
                )
    
    return render(request, "register.html")


def waiting_list(request):
    """Handle waiting list registration form"""
    if request.method == "POST":
        form = WaitingListForm(request.POST)
        if form.is_valid():
            try:
                # Save the form data
                waiting_list_entry = form.save(commit=False)
                
                # Handle the custom desired_endpoints checkboxes
                desired_endpoints = request.POST.getlist('desired_endpoints')
                waiting_list_entry.desired_endpoints = desired_endpoints
                
                # Handle the custom desired_plan radio button
                desired_plan = request.POST.get('desired_plan')
                waiting_list_entry.desired_plan = desired_plan
                # Handle the custom desired_billing_cycle radio button
                desired_billing_cycle = request.POST.get('desired_billing_cycle')
                waiting_list_entry.desired_billing_cycle = desired_billing_cycle
                
                waiting_list_entry.save()
                
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
                        "This email is already on our waiting list. " "We'll notify you when the API becomes available!",
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

    plans = Plan.objects.filter(is_active=True).order_by("price_monthly")
    return render(request, "waiting_list.html", {"form": form, "plans": plans})


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
        validity_days = request.data.get("validity_days", request.user.token_validity_days)

        request.user.regenerate_request_token(save_old=save_old, auto_renew=auto_renew, validity_days=validity_days)

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


def plans_view(request):
    plans = Plan.objects.filter(is_active=True).order_by("price_monthly")
    context = {
        "plans": plans,
        "user": request.user if request.user.is_authenticated else None,
        "current_plan": request.user.current_plan if request.user.is_authenticated else None,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, "subscription/plans.html", context)


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
                return JsonResponse({"error": "This plan is not available for purchase."}, status=400)
            else:
                messages.error(request, "This plan is not available for purchase.")
                return redirect("pricing")

        success_url = request.build_absolute_uri(reverse("subscription-success"))
        cancel_url = request.build_absolute_uri(reverse("home")) + "#pricing"
        session = StripeService.create_checkout_session(user=request.user, plan=plan, success_url=success_url, cancel_url=cancel_url)

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
            messages.error(request, "Service temporarily unavailable. Please try again later.")
            return redirect("home") + "pricing"
    except stripe.error.AuthenticationError as e:
        if is_api_request:
            return JsonResponse({"error": "Authentication error with payment service."}, status=500)
        else:
            messages.error(request, "Payment service error. Please try again later.")
            return redirect("home") + "pricing"
    except stripe.error.StripeError as e:
        if is_api_request:
            return JsonResponse({"error": f"Payment service error: {str(e)}"}, status=400)
        else:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect("home") + "#pricing"
    except Http404:
        raise
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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

        messages.success(request, "Your subscription has been canceled and will not renew.")

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


def stripe_webhook(request):
    logger.debug("Stripe webhook endpoint called.")
    if request.method != "POST":
        logger.debug("Invalid method for webhook, returning 405.")
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    if request.content_type != "application/json":
        logger.debug("Invalid content type for webhook, returning 400.")
        return JsonResponse({"error": "Content-Type must be application/json"}, status=400)

    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
    logger.debug(f"Webhook secret configured: {bool(webhook_secret)}")
    if not webhook_secret:
        logger.error("Webhook secret not configured")
        return JsonResponse({"error": "Webhook secret not configured"}, status=400)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    logger.debug(f"Signature header present: {bool(sig_header)}")

    try:
        logger.debug("Verifying Stripe signature...")
        stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        logger.debug("Signature verification successful.")
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
            'payment_intent.payment_failed': handle_payment_failed,
            'invoice.payment_succeeded': handle_payment_succeeded,
            'customer.subscription.trial_will_end': handle_trial_ending,  # not used by now
            'invoice.payment_action_required': handle_payment_action_required,  # not used by now
        }

        handler = handlers.get(event['type'])
        logger.debug(f"Processing webhook event type: {event['type']}")
        if handler:
            try:
                logger.debug(f"Calling handler for {event['type']}")
                logger.debug(f"Event data: {event['data']['object']}")
                result = handler(event['data']['object'])
                logger.debug(f"Handler result: {result}")
                return JsonResponse({"status": "success", "processed": True, "result": result})
            except Exception as e:
                logger.error(f"Webhook handler error for {event['type']}: {e}")
                return JsonResponse({"status": "error", "message": str(e)}, status=500)
        else:
            logger.debug(f"Unhandled webhook event type: {event['type']}")
            return JsonResponse({"status": "success", "processed": False})

    except Exception as e:
        logger.error(f"Unexpected error in webhook: {e}")
        return JsonResponse({"status": "error"}, status=500)


def handle_subscription_created(subscription_data):
    """Handle new subscription creation"""
    try:
        customer_id = subscription_data['customer']
        subscription_id = subscription_data['id']
        user = User.objects.get(stripe_customer_id=customer_id)

        if user.stripe_subscription_id and user.stripe_subscription_id != subscription_id:
            try:
                old_sub_id = user.stripe_subscription_id
                stripe.Subscription.delete(old_sub_id)
                logger.info(f"Old Subscription canceled: {user.stripe_subscription_id}")
            except Exception as e:
                logger.error(f"Error canceling old subscription: {str(e)}")
        user.stripe_subscription_id = subscription_id

        current_period_start = subscription_data.get('current_period_start')
        current_period_end = subscription_data.get('current_period_end')
        if not current_period_start or not current_period_end:
            items = subscription_data.get('items', {}).get('data', [])
            if items:
                if not current_period_start:
                    current_period_start = items[0].get('current_period_start')
                if not current_period_end:
                    current_period_end = items[0].get('current_period_end')

        if current_period_start:
            user.current_period_start = dt.fromtimestamp(current_period_start, tz=tz.utc)
            user.subscription_started_at = dt.fromtimestamp(current_period_start, tz=tz.utc)
        if current_period_end:
            user.current_period_end = dt.fromtimestamp(current_period_end, tz=tz.utc)
            user.subscription_expires_at = user.current_period_end

        if not subscription_data['items']['data']:
            raise ValueError('Stripe subscription items list is empty, cannot determine price_id.')
        price_id = subscription_data['items']['data'][0]['price']['id']
        try:
            plan = Plan.objects.get(stripe_price_id=price_id)
            user.current_plan = plan
        except Plan.DoesNotExist:
            logger.warning(f"Plan not found for Stripe price ID: {price_id}")

        cache_key = f"payment_succeeded:{customer_id}"
        if cache.get(cache_key):
            user.subscription_status = SubscriptionStatus.ACTIVE
            logger.info(f"Set subscription_status=ACTIVE from cached payment for user_id={user.id}")
        elif user.subscription_status != SubscriptionStatus.ACTIVE:
            user.subscription_status = SubscriptionStatus.INCOMPLETE
        # Clear any payment restrictions
        user.clear_payment_failure_flags(user)
        user.save()

        logger.info(f"Subscription created: user_id={user.id}, subscription_id={subscription_data['id']}")
        return {"user_id": user.id, "subscription_id": subscription_data['id'], "status": user.subscription_status}

    except User.DoesNotExist:
        logger.error(f"User not found for customer ID: {customer_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling subscription creation: {e}")
        return {"error": str(e)}


def handle_subscription_updated(subscription_data):
    """Handle subscription updates with enhanced rate limiting integration"""
    try:
        subscription_id = subscription_data['id']
        logger.debug(f"Processing subscription update for ID: {subscription_id}")
        customer_id = subscription_data['customer']
        user = User.objects.get(stripe_customer_id=customer_id)
        logger.debug(f"Found user {user.id} with subscription {subscription_id}")

        # Update status and dates
        old_status = user.subscription_status
        new_status = subscription_data['status']
        logger.info(f"Subscription status change: user_id={user.id}, {old_status} -> {new_status}")
        user.set_subscription_status(new_status)

        current_period_start = subscription_data.get('current_period_start')
        current_period_end = subscription_data.get('current_period_end')
        if not current_period_start or not current_period_end:
            items = subscription_data.get('items', {}).get('data', [])
            if items:
                if not current_period_start:
                    current_period_start = items[0].get('current_period_start')
                if not current_period_end:
                    current_period_end = items[0].get('current_period_end')

        if current_period_start:
            user.current_period_start = dt.fromtimestamp(current_period_start, tz=tz.utc)
        if current_period_end:
            user.current_period_end = dt.fromtimestamp(current_period_end, tz=tz.utc)
            user.subscription_expires_at = user.current_period_end

        # Handle plan changes
        if subscription_data['items']['data']:
            price_id = subscription_data['items']['data'][0]['price']['id']
            try:
                new_plan = Plan.objects.get(stripe_price_id=price_id)
                if user.current_plan != new_plan:
                    logger.info(f"Plan changed: user_id={user.id}, from {user.current_plan} to {new_plan}")
                    user.current_plan = new_plan
                    # Clear cached limits to force refresh
                    user.limits_cache_updated = None
            except Plan.DoesNotExist:
                logger.warning(f"Plan not found for Stripe price ID: {price_id}")

        # Handle status-specific actions
        if subscription_data['status'] == 'active':
            user.handle_payment_success()
            if old_status in ['past_due', 'incomplete']:
                logger.info(f"Subscription reactivated: user_id={user.id}")
        elif subscription_data['status'] in ['past_due', 'incomplete']:
            user.handle_payment_failure()
            logger.warning(f"Subscription payment issues: user_id={user.id}")
        elif subscription_data['status'] == 'canceled':
            logger.info(f"Subscription canceled: user_id={user.id}, subscription_id={subscription_id}")

        user.save()
        logger.debug(f"User {user.id} saved with new subscription status: {user.subscription_status}")

        # Clear rate limiting cache
        cache = caches['rate_limit']
        cache_key = f"user_limits:{user.id}"
        cache.delete(cache_key)

        logger.debug(f"Subscription update completed for user {user.id}")
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
        customer_id = subscription_data['customer']
        subscription_id = subscription_data['id']
        user = User.objects.get(stripe_customer_id=customer_id)
        if user.stripe_subscription_id != subscription_id:
            logger.info(f"Ignoring status change for outdated subscription: {subscription_id}")
            return {"user_id": user.id, "ignored": True}
        user.cancel_subscription()
        user.clear_payment_failure_flags(user)  # Clear restrictions but subscription is still canceled

        logger.info(f"Subscription canceled: user_id={user.id}, subscription_id={subscription_id}")
        return {"user_id": user.id, "canceled": True}

    except User.DoesNotExist:
        logger.error(f"User not found for canceled subscription: {subscription_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {e}")
        return {"error": str(e)}


def handle_payment_failed(subscription_data):
    """Handle payment failures with progressive restrictions"""
    try:
        subscription_id = subscription_data["id"]
        if not subscription_id:
            return {"error": "No subscription ID in invoice"}

        customer_id = subscription_data['customer']
        user = User.objects.get(stripe_customer_id=customer_id)
        user.handle_payment_failure()
        logger.warning(f"Payment failed: user_id={user.id}")
        return {"user_id": user.id}
    except User.DoesNotExist:
        logger.error(f"User not found for failed payment, subscription: {subscription_id}")
        return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Error handling payment failure: {e}")
        return {"error": str(e)}


def handle_payment_succeeded(subscription_data):
    """Handle successful payments"""
    try:
        subscription_id = subscription_data["id"]
        if not subscription_id:
            logger.info(f"success:" "True", "message:" "No subscription to update")
            return {"success": True, "message": "No subscription to update"}

        customer_id = subscription_data['customer']
        cache_key = f"payment_succeeded:{customer_id}"
        cache.set(cache_key, True, timeout=5)

        user = User.objects.get(stripe_customer_id=customer_id)
        user.handle_payment_success()
        logger.info(f"Payment succeeded: user_id={user.id}")
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
        logger.info(f"Trial ending: user_id={user.id}, subscription_id={subscription_id}")

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
        user.set_payment_failure_flags(user, 'warning')

        logger.info(f"Payment action required: user_id={user.id}")
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
        "current_plan": PlanSerializer(user.current_plan).data if user.current_plan else None,
        "subscription_status": user.subscription_status,
        "subscription_expires_at": user.subscription_expires_at,
        "subscription_days_remaining": user.subscription_days_remaining,
        "is_subscription_active": user.is_subscription_active,
        "daily_request_limit": user.daily_request_limit,
        "daily_requests_made": user.daily_requests_made,
        "requests_remaining": max(0, user.daily_request_limit - user.daily_requests_made),
    }
    return Response(data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_checkout_session_api(request):
    try:
        plan = get_object_or_404(Plan, id=request.data.get("plan_id"), is_active=True)

        if not plan.stripe_price_id:
            return Response({"error": "This plan is not available for purchase."}, status=400)

        session = StripeService.create_checkout_session(
            user=request.user if request.user.is_authenticated else None,
            plan=plan,
            success_url=request.data.get("success_url", request.build_absolute_uri(reverse("subscription-success"))),
            cancel_url=request.data.get("cancel_url", request.build_absolute_uri(reverse("home"))),
        )

        return Response({"checkout_url": session.url, "session_id": session.id})

    except stripe.error.StripeError as e:
        status_code = 503 if "APIConnection" in str(type(e)) else 500 if "Authentication" in str(type(e)) else 400
        error_msg = (
            "Service temporarily unavailable. Please try again later."
            if status_code == 503
            else "Authentication error with payment service."
            if status_code == 500
            else f"Payment service error: {str(e)}"
        )
        return Response({"error": error_msg}, status=status_code)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


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


@csrf_exempt
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def tickers_view(request):
    url = request.query_params.get("url")
    pattern = r'https://[^/]+'
    match = re.search(pattern, url or "")
    try:
        if not match:
            return Response({"error": "No URL received."}, status=400)
        new_url = url.replace(match.group(0), settings.FINANCIAL_DATA_URL)
        return Response({"new_url": new_url})
    except Exception as e:
        logger.error(f"Error replacing domain: {e}")
        return Response({"error": str(e)}, status=500)
