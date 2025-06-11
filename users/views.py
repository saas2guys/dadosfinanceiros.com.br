import json
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

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


def plans_view(request):
    plans = Plan.objects.filter(is_active=True).order_by("price_monthly")
    context = {
        "plans": plans,
        "user": request.user if request.user.is_authenticated else None,
        "current_plan": request.user.current_plan
        if request.user.is_authenticated
        else None,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, "subscription/plans.html", context)


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
                return redirect("plans")

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
            return redirect("plans")
    except Http404:
        raise
    except Exception as e:
        if is_api_request:
            return JsonResponse({"error": str(e)}, status=400)
        else:
            messages.error(request, f"Error creating checkout session: {str(e)}")
            return redirect("plans")


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
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    if request.content_type != "application/json":
        return JsonResponse(
            {"error": "Content-Type must be application/json"}, status=400
        )

    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
    if not webhook_secret:
        return JsonResponse({"error": "Webhook secret not configured"}, status=400)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    try:
        event = json.loads(payload)

        stripe_service = StripeService()
        result = stripe_service.process_webhook_event(event)

        return JsonResponse({"status": "success", "processed": result is not None})

    except Exception as e:
        logger.error(f"Unexpected error in webhook: {e}")
        return JsonResponse({"status": "error"}, status=500)


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
            "cancel_url", request.build_absolute_uri(reverse("plans"))
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
