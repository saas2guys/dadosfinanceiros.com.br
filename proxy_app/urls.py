from django.urls import path, re_path
from . import views

app_name = 'proxy_app'

urlpatterns = [
    # Catch-all proxy pattern - forwards ALL API requests to microservice
    # This MUST be last in the main urls.py to catch remaining paths
    # Use AsyncProxyView for high concurrency or SimpleProxyView for standard load
    re_path(r'^api/(?P<path>.*)$', views.AsyncProxyView.as_view(), name='api_proxy'),
    
    # Alternative for lighter load:
    # re_path(r'^api/(?P<path>.*)$', SimpleProxyView.as_view(), name='api_proxy'),

    # Generic proxy endpoint that forwards all requests to Polygon.io
    re_path(r'^proxy/(?P<path>.*)$', views.AsyncProxyView.as_view(), name='proxy'),
    
    # Specific Polygon.io endpoints
    path('stocks/', views.stocks_list, name='stocks-list'),
    path('stocks/<str:symbol>/', views.stock_details, name='stock-details'),
    path('stocks/<str:symbol>/trades/', views.stock_trades, name='stock-trades'),
] 