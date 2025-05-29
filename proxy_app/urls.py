from django.urls import path, re_path

from .views import PolygonProxyView

app_name = "proxy_app"

urlpatterns = [
    re_path(r'^(?P<path>.*)$', PolygonProxyView.as_view(), name='polygon_proxy'),
]
