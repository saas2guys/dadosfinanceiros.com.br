import logging
import re

import requests
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission

logger = logging.getLogger(__name__)


@permission_classes([AllowAny])
def api_documentation(request):
    return render(request, "api/docs.html")


class PolygonProxyView(APIView):
    renderer_classes = [JSONRenderer]
    authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
    permission_classes = [IsAuthenticated, DailyLimitPermission]

    V2_ENDPOINTS = [
        "aggs", "snapshot/locale/us/markets", "last/trade", "last/nbbo",
        "fed/vx/treasury-yields", "benzinga/v1/ratings", "grouped/locale/us/market"
    ]
    
    V1_ENDPOINTS = [
        "conversion", "open-close", "related-companies", "meta/symbols",
        "meta/exchanges", "historic/trades", "historic/quotes", "last/currencies"
    ]
    
    EXCLUDED_HEADERS = {
        "host", "connection", "content-length", "authorization", "x-request-token"
    }
    
    PAGINATION_FIELDS = ["next_url", "previous_url", "next", "previous", "first_url", "last_url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_configuration()
        self._setup_local_environment()

    def _setup_configuration(self):
        self.base_url = settings.POLYGON_BASE_URL
        self.api_key = settings.POLYGON_API_KEY
        self.timeout = getattr(settings, "PROXY_TIMEOUT", 30)
        self.proxy_domain = getattr(settings, "PROXY_DOMAIN", "api.dadosfinanceiros.com.br")
        self.session = requests.Session()

    def _setup_local_environment(self):
        if settings.ENV == "local":
            logger.info("Using no auth and no permissions for local environment!")
            self.authentication_classes = []
            self.permission_classes = [AllowAny]

    def _get_polygon_version(self, path):
        for endpoint in self.V2_ENDPOINTS:
            if endpoint in path:
                return "v2"
        
        for endpoint in self.V1_ENDPOINTS:
            if endpoint in path:
                return "v1"
        
        return "v3"

    def _build_target_url(self, path):
        clean_path = path.replace("v1/", "")
        
        if clean_path.startswith(("fed/", "benzinga/")):
            return f"{self.base_url}/{clean_path}"
        
        version = self._get_polygon_version(clean_path)
        
        if self._needs_snapshot_prefix(clean_path):
            clean_path = f"snapshot/locale/us/markets/{clean_path.split('snapshot/')[-1]}"
        
        return f"{self.base_url}/{version}/{clean_path}"

    def _needs_snapshot_prefix(self, path):
        return "snapshot" in path and not path.startswith("snapshot/locale")

    def _clean_headers(self, request_headers):
        return {
            k: v for k, v in request_headers.items()
            if k.lower() not in self.EXCLUDED_HEADERS
        }

    def _get_user_info(self, request):
        if hasattr(request, "user") and request.user.is_authenticated:
            return getattr(request.user, "email", str(request.user))
        return "anonymous"

    def _replace_polygon_urls(self, data, request):
        if not isinstance(data, dict):
            return data

        for field in self.PAGINATION_FIELDS:
            if self._has_polygon_url(data, field):
                data[field] = self._transform_url(data[field])
                logger.debug(f"Replaced {field}: {data[field]}")

        return data

    def _has_polygon_url(self, data, field):
        return (field in data and 
                isinstance(data[field], str) and 
                "polygon.io" in data[field])

    def _transform_url(self, url):
        url = re.sub(r"[?&]apikey=[^&]*&?", "", url, flags=re.IGNORECASE)
        url = re.sub(r"[&?]+$", "", url)
        url = re.sub(r"&+", "&", url)
        url = url.replace("api.polygon.io", self.proxy_domain)
        url = self._ensure_https(url)
        url = re.sub(r"/v[2-3]/", "/v1/", url)
        return url

    def _ensure_https(self, url):
        if url.startswith("http://"):
            return url.replace("http://", "https://")
        elif not url.startswith("https://"):
            return f"https://{url}"
        return url

    def _make_request(self, method, url, params, headers, data=None):
        return self.session.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json=data,
            timeout=self.timeout
        )

    def _handle_request(self, request, path):
        try:
            target_url = self._build_target_url(path)
            params = {**request.GET.dict(), "apiKey": self.api_key}
            headers = self._clean_headers(request.headers)
            user_info = self._get_user_info(request)

            logger.info(f"Forwarding {request.method} request to: {target_url} by user: {user_info}")
            logger.info(f"With params: {params}")

            json_data = request.data if request.method in ["POST", "PUT", "PATCH"] else None
            response = self._make_request(request.method, target_url, params, headers, json_data)

            logger.info(f"Response status code: {response.status_code}")
            return self._process_response(response, request)

        except requests.Timeout:
            return self._error_response("Gateway Timeout", "The request to Polygon.io timed out", 
                                      status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.RequestException as e:
            return self._error_response("Bad Gateway", str(e), status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return self._error_response("Internal Server Error", str(e), 
                                      status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_response(self, response, request):
        try:
            data = response.json() if response.content else {}
            
            if data:
                data = self._replace_polygon_urls(data, request)
                # Remove Polygon.io specific fields that shouldn't be exposed to users
                data.pop("status", None)
                data.pop("request_id", None)
                data.pop("queryCount", None)

            return Response(data=data, status=response.status_code)
            
        except ValueError:
            if response.status_code == 404:
                return self._error_response("Not Found", "The requested resource was not found", 
                                          status.HTTP_404_NOT_FOUND)
            return Response(
                data={"error": "Invalid JSON response", "content": response.text},
                status=response.status_code
            )

    def _error_response(self, error, message, status_code):
        logger.error(f"{error}: {message}")
        return Response({"error": error, "message": message}, status=status_code)

    def get(self, request, path):
        return self._handle_request(request, path)

    def post(self, request, path):
        return self._handle_request(request, path)

    def put(self, request, path):
        return self._handle_request(request, path)

    def delete(self, request, path):
        return self._handle_request(request, path)
