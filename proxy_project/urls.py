from django.conf import settings
from django.conf.urls.i18n import i18n_patterns, set_language
from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from sitemaps import sitemaps

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("set_language/", set_language, name="set_language"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', lambda r: HttpResponse("User-agent: *\nAllow: /\nSitemap: https://api.dadosfinanceiros.com.br/sitemap.xml", content_type="text/plain")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("v1/", include("proxy_app.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    prefix_default_language=False,
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
