from django.urls import path, re_path

from .views import UnifiedFinancialAPIView, api_documentation
from .views_new import FinancialAPIView, HealthView, EndpointsView

app_name = "proxy_app"

urlpatterns = [
    # API Documentation - available at /api/docs/
    path("docs/", api_documentation, name="api_docs"),
    
    # Health check and documentation endpoints
    path("health/", HealthView.as_view(), name="health"),
    path("api/v1/endpoints/", EndpointsView.as_view(), name="endpoints"),
    
    # New unified API using the proxy system
    re_path(r"^api/v1/(?P<path>.*)$", FinancialAPIView.as_view(), name="unified_financial_api_new"),
    
    # Backward compatibility - all other requests go to original implementation
    re_path(
        r"^(?!docs/|health/|api/)(?P<path>.*)$",
        UnifiedFinancialAPIView.as_view(),
        name="unified_financial_api_legacy",
    ),
]
