from aiohttp.web_response import json_response
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns, set_language
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

import users.views
from proxy_app.views import api_documentation
from users.views import stripe_webhook

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("set_language/", set_language, name="set_language"),
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # path(
    #     'robots.txt',
    #     lambda r: HttpResponse("User-agent: *\nAllow: /\nSitemap: https://api.financialdata.online/sitemap.xml", content_type="text/plain"),
    # ),
    # API Documentation - accessible without language prefix
    path("api/docs/", api_documentation, name="api_docs_direct"),
    # Stripe webhooks should not have language prefix
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
    # API endpoints - accessible without language prefix
    path("v1/", include("proxy_app.urls", namespace="proxy_app_legacy")),
    path("api/v1/", include("proxy_app.urls", namespace="proxy_app")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # User API endpoints - accessible without language prefix
    path("api/register/", users.views.RegisterView.as_view(), name="api_register"),
    path("api/profile/", users.views.UserProfileView.as_view(), name="api_profile"),
    path("api/regenerate-token/", users.views.RegenerateRequestTokenView.as_view(), name="api_regenerate_token"),
    path("api/token-history/", users.views.TokenHistoryView.as_view(), name="api_token_history"),
    path("api/plans/", users.views.PlansListView.as_view(), name="api_plans"),
    path("api/subscription/", users.views.user_subscription, name="api_user_subscription"),
    path("api/create-checkout-session/", users.views.create_checkout_session_api, name="api_create_checkout_session"),
    # Main content URLs - accessible without language prefix
    path("", include("users.urls")),
]

# Admin URLs with language prefix for security
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    prefix_default_language=True,
)

# Add debug toolbar URLs for development
if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        # debug_toolbar not installed, skip it
        pass
