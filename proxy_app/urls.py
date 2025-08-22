from django.http import JsonResponse
from django.urls import path, re_path

from .views import UnifiedFinancialAPIView, api_documentation
from .views_new import EndpointsView, FinancialAPIView, HealthView

app_name = "proxy_app"

def root():
    return JsonResponse({"status": "ok"}, status=200)

urlpatterns = [
    path("", root, name="root"),
    path("health/", root, name="health"),
    # API Documentation - available at /api/docs/
    path("docs/", api_documentation, name="api_docs"),
    path("api/v1/endpoints/", EndpointsView.as_view(), name="endpoints"),
    # New unified API using the proxy system
    re_path(r"^api/v1/(?P<path>.*)$", FinancialAPIView.as_view(), name="unified_financial_api_new"),
    # Backward compatibility - all other requests go to original implementation
    re_path(
        r"^(?!docs/|api/)(?P<path>.*)$",
        UnifiedFinancialAPIView.as_view(),
        name="unified_financial_api_legacy",
    ),
]
