from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("register/", views.register_user, name="register"),
    path("regenerate-token/", views.regenerate_token, name="regenerate_token"),
    
    # Subscription URLs
    path("plans/", views.plans_view, name="plans"),
    path("create-checkout-session/", views.create_checkout_session, name="create_checkout_session"),
    path("subscription/success/", views.subscription_success, name="subscription_success"),
    path("cancel-subscription/", views.cancel_subscription, name="cancel_subscription"),
    path("reactivate-subscription/", views.reactivate_subscription, name="reactivate_subscription"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    
    # API URLs
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", views.RegisterView.as_view(), name="api_register"),
    path("api/profile/", views.UserProfileView.as_view(), name="api_profile"),
    path(
        "api/regenerate-token/",
        views.RegenerateRequestTokenView.as_view(),
        name="api_regenerate_token",
    ),
    path(
        "api/token-history/", views.TokenHistoryView.as_view(), name="api_token_history"
    ),
    
    # Subscription API URLs
    path("api/plans/", views.PlansListView.as_view(), name="api_plans"),
    path("api/subscription/", views.user_subscription, name="api_user_subscription"),
    path("api/create-checkout-session/", views.create_checkout_session_api, name="api_create_checkout_session"),
]
