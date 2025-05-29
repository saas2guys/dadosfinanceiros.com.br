from django.contrib import admin
from django.urls import path, re_path
from proxy_app.views import PolygonProxyView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    re_path(r'^v1/(?P<path>.*)$', PolygonProxyView.as_view(), name='polygon_proxy'),
]
