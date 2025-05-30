from django.urls import path, re_path
from django.shortcuts import redirect

from .views import PolygonProxyView, api_documentation

app_name = "proxy_app"

urlpatterns = [
    path("docs/", api_documentation, name="api_docs"),
    
    # New unified pattern with market selector
    re_path(
        r"^(?P<market>us|br)/(?P<path>.*)$", 
        PolygonProxyView.as_view(), 
        name="unified_proxy"
    ),
    
    # Backward compatibility: redirect old format to US market
    re_path(
        r"^(?!docs/)(?!us/)(?!br/)(?P<path>.*)$", 
        lambda request, path: redirect(f'/v1/us/{path}', permanent=False), 
        name="legacy_proxy_redirect"
    ),
]
