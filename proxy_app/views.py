import logging
import re
from datetime import datetime, timedelta, timezone

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

def get_permission_classes():
    if settings.ENV == "local":
        return [AllowAny]
    return [IsAuthenticated, DailyLimitPermission]

def get_authentication_classes():
    if settings.ENV == "local":
        return []
    return [JWTAuthentication, RequestTokenAuthentication]

_permissions = get_permission_classes()
_authentications = get_authentication_classes()

@permission_classes(_permissions)
def api_documentation(request):
    return render(request, "api/docs.html")


class PolygonProxyView(APIView):

    renderer_classes = [JSONRenderer]
    authentication_classes = _authentications
    permission_classes = _permissions

    VERSION_PATTERNS = {
        "v3": [
            "reference/tickers/types",
            "reference/tickers/",
            "reference/tickers",
            "reference/options/",
            "reference/indices/",
            "trades/",
            "quotes/",
        ],
        "v2": [
            "aggs/",
            "snapshot/locale/us/markets/",
            "last/trade/",
            "last/nbbo/",
        ],
        "v1": [
            "open-close/",
            "conversion/",
            "indicators/",
            "meta/symbols/",
        ],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = settings.POLYGON_BASE_URL
        self.api_key = settings.POLYGON_API_KEY
        self.timeout = getattr(settings, "PROXY_TIMEOUT", 30)
        self.proxy_domain = getattr(
            settings, "PROXY_DOMAIN", "api.dadosfinanceiros.com.br"
        )
        self.session = requests.Session()

        if settings.ENV == "local":
            self.authentication_classes = []
            self.permission_classes = [AllowAny]

    def _proxy_request(self, request, path):
        try:
            clean_path = path[3:] if path.startswith("v1/") else path
            version = self._get_version(clean_path)

            target_url = f"{self.base_url}/{version}/{clean_path}"

            params = {**request.GET.dict(), "apiKey": self.api_key}
            headers = {
                k: v
                for k, v in request.headers.items()
                if k.lower()
                not in {
                    "host",
                    "connection",
                    "content-length",
                    "authorization",
                    "x-request-token",
                }
            }
            json_data = (
                request.data if request.method in ["POST", "PUT", "PATCH"] else None
            )

            response = self.session.request(
                method=request.method,
                url=target_url,
                params=params,
                headers=headers,
                json=json_data,
                timeout=self.timeout,
            )

            try:
                data = response.json() if response.content else {}
                if data:
                    data = self._clean_response(data)
                return Response(data=data, status=response.status_code)
            except ValueError:
                return Response(
                    {"error": "Invalid JSON response", "content": response.text},
                    status=response.status_code,
                )

        except requests.Timeout:
            return Response({"error": "Gateway Timeout"}, status=504)
        except requests.RequestException as e:
            return Response({"error": "Bad Gateway", "message": str(e)}, status=502)
        except Exception as e:
            logger.error(f"Proxy error: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=500)

    def _get_version(self, path):
        if path == "snapshot" or (path.startswith("snapshot?")):
            return "v3"

        for version, patterns in self.VERSION_PATTERNS.items():
            for pattern in patterns:
                if (pattern.endswith("/") and path.startswith(pattern)) or (
                    path == pattern or path.startswith(pattern + "/")
                ):
                    return version
        return "v3"

    def _clean_response(self, data):
        if not isinstance(data, dict):
            return data

        for field in ["status", "request_id", "queryCount"]:
            data.pop(field, None)

        for field in ["next_url", "previous_url", "next", "previous"]:
            if (
                field in data
                and isinstance(data[field], str)
                and "polygon.io" in data[field]
            ):
                url = data[field].replace("api.polygon.io", self.proxy_domain)
                url = re.sub(r"[?&]apikey=[^&]*&?", "", url, flags=re.IGNORECASE)
                url = re.sub(r"/v[1-3]/", "/v1/", url)
                url = re.sub(r"[&?]+$", "", url)
                if not url.startswith("https://"):
                    url = (
                        f"https://{url}"
                        if not url.startswith("http")
                        else url.replace("http://", "https://")
                    )
                data[field] = url

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self._clean_response(value)
            elif isinstance(value, list):
                data[key] = [
                    self._clean_response(item) if isinstance(item, dict) else item
                    for item in value
                ]

        return data

    def get(self, request, path):
        return self._proxy_request(request, path)

    def post(self, request, path):
        return self._proxy_request(request, path)

    def put(self, request, path):
        return self._proxy_request(request, path)

    def delete(self, request, path):
        return self._proxy_request(request, path)
