from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

# API URL patterns
api_urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterView.as_view(), name="api_register"),
    path("profile/", views.UserProfileView.as_view(), name="api_profile"),
    path(
        "regenerate-token/",
        views.RegenerateRequestTokenView.as_view(),
        name="api_regenerate_token",
    ),
    path("token-history/", views.TokenHistoryView.as_view(), name="api_token_history"),
    path("plans/", views.PlansListView.as_view(), name="api_plans"),
    path("subscription/", views.user_subscription, name="user-subscription"),
    path(
        "create-checkout-session/",
        views.create_checkout_session_api,
        name="api_create_checkout_session",
    ),
    path("tickers/", views.tickers_view, name="api_tickers"),
]

# SEO-optimized landing pages for different financial data types
seo_landing_pages = [
    # Stock Market API
    path("stock-market-api/", TemplateView.as_view(template_name="stock_market_api.html"), name="stock_market_api"),
    path("stocks-api/", TemplateView.as_view(template_name="stock_market_api.html"), name="stocks_api"),
    path("equity-data-api/", TemplateView.as_view(template_name="stock_market_api.html"), name="equity_data_api"),
    # Forex API
    path("forex-api/", TemplateView.as_view(template_name="forex_api.html"), name="forex_api"),
    path("currency-api/", TemplateView.as_view(template_name="forex_api.html"), name="currency_api"),
    path("fx-api/", TemplateView.as_view(template_name="forex_api.html"), name="fx_api"),
    # Crypto API
    path("crypto-api/", TemplateView.as_view(template_name="crypto_api.html"), name="crypto_api"),
    path("cryptocurrency-api/", TemplateView.as_view(template_name="crypto_api.html"), name="cryptocurrency_api"),
    path("bitcoin-api/", TemplateView.as_view(template_name="crypto_api.html"), name="bitcoin_api"),
    path("digital-assets-api/", TemplateView.as_view(template_name="crypto_api.html"), name="digital_assets_api"),
    # Options API
    path("options-api/", TemplateView.as_view(template_name="options_api.html"), name="options_api"),
    path("derivatives-api/", TemplateView.as_view(template_name="options_api.html"), name="derivatives_api"),
    # Indices API
    path("indices-api/", TemplateView.as_view(template_name="indices_api.html"), name="indices_api"),
    path("index-api/", TemplateView.as_view(template_name="indices_api.html"), name="index_api"),
    path("market-indices-api/", TemplateView.as_view(template_name="indices_api.html"), name="market_indices_api"),
    # Futures API
    path("futures-api/", TemplateView.as_view(template_name="futures_api.html"), name="futures_api"),
    # Commodities API
    path("commodities-api/", TemplateView.as_view(template_name="commodities_api.html"), name="commodities_api"),
    path("commodity-data-api/", TemplateView.as_view(template_name="commodities_api.html"), name="commodity_data_api"),
    # Economic Indicators API
    path("economic-indicators-api/", TemplateView.as_view(template_name="economic_indicators_api.html"), name="economic_indicators_api"),
    path("economic-data-api/", TemplateView.as_view(template_name="economic_indicators_api.html"), name="economic_data_api"),
    path("macro-data-api/", TemplateView.as_view(template_name="economic_indicators_api.html"), name="macro_data_api"),
    # Fundamentals API
    path("fundamentals-api/", TemplateView.as_view(template_name="fundamentals_api.html"), name="fundamentals_api"),
    path("financial-statements-api/", TemplateView.as_view(template_name="fundamentals_api.html"), name="financial_statements_api"),
    # News API
    path("news-api/", TemplateView.as_view(template_name="news_api.html"), name="news_api"),
    path("news-sentiment-api/", TemplateView.as_view(template_name="news_api.html"), name="news_sentiment_api"),
    path("financial-news-api/", TemplateView.as_view(template_name="news_api.html"), name="financial_news_api"),
    # Technical Analysis API
    path("technical-analysis-api/", TemplateView.as_view(template_name="technical_analysis_api.html"), name="technical_analysis_api"),
    path("technical-indicators-api/", TemplateView.as_view(template_name="technical_analysis_api.html"), name="technical_indicators_api"),
    path("ta-api/", TemplateView.as_view(template_name="technical_analysis_api.html"), name="ta_api"),
    # Earnings API
    path("earnings-api/", TemplateView.as_view(template_name="earnings_api.html"), name="earnings_api"),
    path("earnings-calendar-api/", TemplateView.as_view(template_name="earnings_api.html"), name="earnings_calendar_api"),
    path("earnings-data-api/", TemplateView.as_view(template_name="earnings_api.html"), name="earnings_data_api"),
]

# User management and authentication URLs
user_management_urls = [
    path("profile/", views.profile, name="profile"),
    path("register/", views.register_user, name="register"),
    path("waiting-list/", views.waiting_list, name="waiting_list"),
    path("waiting-list/success/", views.waiting_list_success, name="waiting_list_success"),
    path("regenerate-token/", views.regenerate_token, name="regenerate_token"),
]

# Authentication URLs
auth_urls = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html", redirect_authenticated_user=True),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    # Password reset URLs
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]

# Subscription URLs
subscription_urls = [
    path(
        "create-checkout-session/",
        views.create_checkout_session,
        name="create-checkout-session",
    ),
    path("subscription/success/", views.subscription_success, name="subscription-success"),
    path("cancel-subscription/", views.cancel_subscription, name="cancel-subscription"),
    path(
        "reactivate-subscription/",
        views.reactivate_subscription,
        name="reactivate-subscription",
    ),
]

# Other content pages
content_urls = [
    path("", views.home, name="home"),
    path("products/", TemplateView.as_view(template_name="products.html"), name="products"),
    path("faq/", TemplateView.as_view(template_name="faq.html"), name="faq"),
    path("blog/", TemplateView.as_view(template_name="blog.html"), name="blog"),
]

# API endpoints (standalone for backward compatibility)
legacy_api_urls = [
    path("api/plans/", views.PlansListView.as_view(), name="api_plans"),
]

urlpatterns = (
    content_urls
    + seo_landing_pages
    + user_management_urls
    + auth_urls
    + subscription_urls
    + legacy_api_urls
    + [path("api/", include((api_urlpatterns, "api"), namespace="api"))]
)
