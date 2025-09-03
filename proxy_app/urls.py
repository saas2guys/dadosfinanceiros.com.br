from django.http import JsonResponse
from django.urls import include, path, re_path

from .views import api_documentation
from .views_new import HealthView

app_name = "proxy_app"

def root():
    return JsonResponse({"status": "ok"}, status=200)

urlpatterns = [
    path("", root, name="root"),
    path("health/", root, name="health"),
    # API Documentation - available at /api/docs/
    path("docs/", api_documentation, name="api_docs"),
    # Provider 1:1 endpoints (placed before catch-all)
    path("", include("proxy_app.provider_api.urls")),
]
