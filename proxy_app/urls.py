from django.urls import path, re_path

from .views import PolygonProxyView, api_documentation

app_name = "proxy_app"

urlpatterns = [
    path("docs/", api_documentation, name="api_docs"),
    re_path(
        r"^(?!docs/)(?P<path>.*)$", PolygonProxyView.as_view(), name="polygon_proxy"
    ),
]
