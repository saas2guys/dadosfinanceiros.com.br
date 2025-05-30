from datetime import timedelta
from decimal import Decimal
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache

from .models import Plan, TokenHistory, User
from .serializers import (
    PlanSerializer,
    TokenHistorySerializer,
    TokenRegenerationSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .stripe_service import StripeService

# Configure Stripe and logger
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.data['message'] = 'User registered successfully'
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class RegenerateRequestTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
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
            'new_token': str(user.request_token),
            'message': 'Token regenerated successfully',
            'token_info': token_info
        }
        return Response(response_data, status=status.HTTP_200_OK)


class TokenHistoryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        
        # Get token history data
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

    context = {
        "token_info": token_info,
        "token_history": _token_history,
        "user": request.user,
        "daily_usage": {
            "made": request.user.daily_requests_made,
            "limit": request.user.daily_request_limit,
            "remaining": request.user.daily_request_limit
            - request.user.daily_requests_made,
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
def register_user(request):
    if request.content_type == "application/json":

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            user.request_token_created = timezone.now()
            user.request_token_expires = user.request_token_created + timedelta(
                days=user.token_validity_days
            )
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:

        if request.method == "GET":
            return render(request, "register.html")
        elif request.method == "POST":
            serializer = UserRegistrationSerializer(data=request.POST)
            if serializer.is_valid():
                user = serializer.save()

                user.request_token_created = timezone.now()
                user.request_token_expires = user.request_token_created + timedelta(
                    days=user.token_validity_days
                )
                user.save()
                login(request, user)
                messages.success(request, "Registration successful! Welcome!")
                return redirect("profile")
            else:
                for field, errors in serializer.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
                return render(request, "register.html")
        return None


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def token_history(request):
    history = TokenHistory.objects.filter(user=request.user).order_by("-created_at")[:5]
    serializer = TokenHistorySerializer(history, many=True)
    
    response_data = {
        "results": serializer.data,
        "current_token": request.user.get_token_info(),
        "previous_tokens": request.user.previous_tokens,
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


# Subscription and Plan Management Views

class PlansListView(generics.ListAPIView):
    """List all available subscription plans"""
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


def plans_view(request):
    """Display available plans and user's current subscription"""
    plans = Plan.objects.filter(is_active=True).order_by('price_monthly')
    context = {
        'plans': plans,
        'user': request.user if request.user.is_authenticated else None,
        'current_plan': request.user.current_plan if request.user.is_authenticated else None,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'subscription/plans.html', context)


@login_required
@require_POST
def create_checkout_session(request):
    """Create Stripe checkout session for subscription"""
    try:
        # Check if this is a JSON API request
        is_api_request = request.content_type == 'application/json'
        
        if is_api_request:
            import json
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
        else:
            plan_id = request.POST.get('plan_id')
            
        plan = get_object_or_404(Plan, id=plan_id, is_active=True)
        
        if plan.is_free:
            # Handle free plan upgrade directly
            request.user.upgrade_to_plan(plan)
            if is_api_request:
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully upgraded to {plan.name} plan!'
                })
            else:
                messages.success(request, f"Successfully upgraded to {plan.name} plan!")
                return redirect('profile')
        
        if not plan.stripe_price_id:
            if is_api_request:
                return JsonResponse({
                    'error': 'This plan is not available for purchase.'
                }, status=400)
            else:
                messages.error(request, "This plan is not available for purchase.")
                return redirect('plans')
        
        # Create Stripe checkout session
        success_url = request.build_absolute_uri(reverse('subscription_success'))
        cancel_url = request.build_absolute_uri(reverse('plans'))
        
        session = StripeService.create_checkout_session(
            user=request.user,
            plan=plan,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        if is_api_request:
            return JsonResponse({
                'checkout_url': session.url,
                'session_id': session.id
            })
        else:
            return redirect(session.url, code=303)
        
    except stripe.error.APIConnectionError as e:
        if is_api_request:
            return JsonResponse({
                'error': 'Service temporarily unavailable. Please try again later.'
            }, status=503)
        else:
            messages.error(request, "Service temporarily unavailable. Please try again later.")
            return redirect('plans')
    except stripe.error.AuthenticationError as e:
        if is_api_request:
            return JsonResponse({
                'error': 'Authentication error with payment service.'
            }, status=500)
        else:
            messages.error(request, "Payment service error. Please try again later.")
            return redirect('plans')
    except stripe.error.StripeError as e:
        if is_api_request:
            return JsonResponse({
                'error': f'Payment service error: {str(e)}'
            }, status=400)
        else:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('plans')
    except Http404:
        # Re-raise Http404 to let Django handle it properly
        raise
    except Exception as e:
        if is_api_request:
            return JsonResponse({
                'error': str(e)
            }, status=400)
        else:
            messages.error(request, f"Error creating checkout session: {str(e)}")
            return redirect('plans')


@login_required
def subscription_success(request):
    """Handle successful subscription payment"""
    return render(request, 'subscription_success.html')


@login_required
@require_POST
def cancel_subscription(request):
    """Cancel user's subscription"""
    try:
        if not request.user.stripe_subscription_id:
            messages.error(request, "No active subscription to cancel.")
            return redirect('profile')
        
        StripeService.cancel_subscription(request.user.stripe_subscription_id)
        request.user.cancel_subscription()
        
        messages.success(request, "Your subscription has been canceled and will not renew.")
        
    except Exception as e:
        messages.error(request, f"Error canceling subscription: {str(e)}")
    
    return redirect('profile')


@login_required
@require_POST
def reactivate_subscription(request):
    """Reactivate a canceled subscription"""
    try:
        if not request.user.stripe_subscription_id:
            messages.error(request, "No subscription to reactivate.")
            return redirect('profile')
        
        StripeService.reactivate_subscription(request.user.stripe_subscription_id)
        
        if request.user.reactivate_subscription():
            messages.success(request, "Your subscription has been reactivated!")
        else:
            messages.error(request, "Unable to reactivate subscription.")
        
    except Exception as e:
        messages.error(request, f"Error reactivating subscription: {str(e)}")
    
    return redirect('profile')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    # Validate content type
    if request.content_type != 'application/json':
        return HttpResponse(status=400)
        
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Check if webhook secret is configured
    if not getattr(settings, 'STRIPE_WEBHOOK_SECRET', None):
        return HttpResponse(status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)
    except AttributeError:
        # Missing webhook secret
        return HttpResponse(status=400)
    
    # Simple replay attack protection - check if we've already processed this event
    event_id = event.get('id')
    if event_id and cache.get(f'stripe_event_{event_id}'):
        return HttpResponse(status=200)  # Already processed, return success
    
    # Mark event as processed (cache for 24 hours)
    if event_id:
        cache.set(f'stripe_event_{event_id}', True, timeout=86400)
    
    # Handle the event
    try:
        if event['type'] == 'checkout.session.completed':
            # Check if event has required data structure
            if 'data' not in event or 'object' not in event['data']:
                return HttpResponse(status=400)
                
            session = event['data']['object']
            # Only handle successful payments
            if session.get('payment_status') == 'paid':
                try:
                    StripeService.handle_successful_payment(session)
                except Exception as e:
                    # Log the error but don't fail the webhook
                    print(f"Unexpected error handling successful payment: {e}")
                    return HttpResponse(status=200)
            
        elif event['type'] == 'customer.subscription.updated':
            if 'data' not in event or 'object' not in event['data']:
                return HttpResponse(status=400)
            subscription = event['data']['object']
            StripeService.handle_subscription_updated(subscription)
            
        elif event['type'] == 'customer.subscription.deleted':
            if 'data' not in event or 'object' not in event['data']:
                return HttpResponse(status=400)
            subscription = event['data']['object']
            StripeService.handle_subscription_deleted(subscription)
            
        elif event['type'] == 'customer.subscription.created':
            if 'data' not in event or 'object' not in event['data']:
                return HttpResponse(status=400)
            subscription = event['data']['object']
            StripeService.handle_subscription_updated(subscription)
            
        elif event['type'] == 'customer.subscription.trial_will_end':
            if 'data' not in event or 'object' not in event['data']:
                return HttpResponse(status=400)
            subscription = event['data']['object']
            StripeService.handle_subscription_updated(subscription)
            
    except KeyError:
        # Missing required event data
        return HttpResponse(status=400)
    except Exception as e:
        # Log unexpected errors but still return success to Stripe
        print(f"Unexpected error in webhook: {e}")
        return HttpResponse(status=200)
        
    return HttpResponse(status=200)


# API Views for subscription management

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_subscription(request):
    """Get user's current subscription details"""
    user = request.user
    data = {
        'current_plan': PlanSerializer(user.current_plan).data if user.current_plan else None,
        'subscription_status': user.subscription_status,
        'subscription_expires_at': user.subscription_expires_at,
        'subscription_days_remaining': user.subscription_days_remaining,
        'is_subscription_active': user.is_subscription_active,
        'daily_request_limit': user.daily_request_limit,
        'daily_requests_made': user.daily_requests_made,
        'requests_remaining': max(0, user.daily_request_limit - user.daily_requests_made),
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session_api(request):
    """Create Stripe checkout session via API"""
    try:
        plan_id = request.data.get('plan_id')
        plan = get_object_or_404(Plan, id=plan_id, is_active=True)
        
        if plan.is_free:
            request.user.upgrade_to_plan(plan)
            return Response({
                'success': True,
                'message': f'Successfully upgraded to {plan.name} plan!'
            })
        
        if not plan.stripe_price_id:
            return Response({
                'error': 'This plan is not available for purchase.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success_url = request.data.get('success_url', 
                                      request.build_absolute_uri(reverse('subscription-success')))
        cancel_url = request.data.get('cancel_url', 
                                     request.build_absolute_uri(reverse('plans')))
        
        session = StripeService.create_checkout_session(
            user=request.user,
            plan=plan,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return Response({
            'checkout_url': session.url,
            'session_id': session.id
        })
        
    except stripe.error.APIConnectionError as e:
        return Response({
            'error': 'Service temporarily unavailable. Please try again later.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except stripe.error.AuthenticationError as e:
        return Response({
            'error': 'Authentication error with payment service.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except stripe.error.StripeError as e:
        return Response({
            'error': f'Payment service error: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
