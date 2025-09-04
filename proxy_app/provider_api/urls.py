from __future__ import annotations


from .provider_urls_fmp import urlpatterns as fmp_urlpatterns
from .provider_urls_polygon import urlpatterns as polygon_urlpatterns

urlpatterns = []
urlpatterns += fmp_urlpatterns
urlpatterns += polygon_urlpatterns
