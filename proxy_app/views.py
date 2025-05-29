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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = settings.POLYGON_BASE_URL
        self.api_key = settings.POLYGON_API_KEY
        self.timeout = getattr(settings, "PROXY_TIMEOUT", 30)
        self.session = requests.Session()
        self.proxy_domain = getattr(
            settings, "PROXY_DOMAIN", "api.dadosfinanceiros.com.br"
        )
        if settings.ENV == "local":
            logger.info("Using no auth and no permissions for local environment!")
            self.authentication_classes = []
            self.permission_classes = [AllowAny]

    def _get_polygon_version(self, path):
        version = "v3"

        if any(
            endpoint in path
            for endpoint in [
                "aggs",
                "snapshot/locale/us/markets",
                "last/trade",
                "last/nbbo",
                "fed/vx/treasury-yields",
                "benzinga/v1/ratings",
                "grouped/locale/us/market",
            ]
        ):
            version = "v2"

        elif any(
            endpoint in path
            for endpoint in [
                "conversion",
                "open-close",
                "related-companies",
                "meta/symbols",
                "meta/exchanges",
                "historic/trades",
                "historic/quotes",
                "last/currencies",
            ]
        ):
            version = "v1"

        return version

    def _get_target_url(self, path):
        clean_path = path.replace("v1/", "")

        if clean_path.startswith("fed/") or clean_path.startswith("benzinga/"):
            return f"{self.base_url}/{clean_path}"

        polygon_version = self._get_polygon_version(clean_path)

        if "snapshot" in clean_path and not clean_path.startswith("snapshot/locale"):
            clean_path = (
                f"snapshot/locale/us/markets/{clean_path.split('snapshot/')[-1]}"
            )

        return f"{self.base_url}/{polygon_version}/{clean_path}"

    def _replace_polygon_urls(self, data, request):
        if not isinstance(data, dict):
            return data

        pagination_fields = ["next_url", "previous_url", "next", "previous"]

        for field in pagination_fields:
            if (
                field in data
                and isinstance(data[field], str)
                and "polygon.io" in data[field]
            ):
                original_url = data[field]

                modified_url = re.sub(
                    r"[?&]apikey=[^&]*&?", "", original_url, flags=re.IGNORECASE
                )
                modified_url = re.sub(r"[&?]+$", "", modified_url)
                modified_url = re.sub(r"&+", "&", modified_url)

                modified_url = modified_url.replace("api.polygon.io", self.proxy_domain)

                if modified_url.startswith("http://"):
                    modified_url = modified_url.replace("http://", "https://")
                elif not modified_url.startswith("https://"):
                    modified_url = f"https://{modified_url}"

                modified_url = re.sub(r"/v[2-3]/", "/v1/", modified_url)

                data[field] = modified_url
                logger.debug(f"Replaced {field}: {original_url} -> {modified_url}")

        return data

    def _handle_request(self, request, path):
        try:
            target_url = self._get_target_url(path)
            params = {**request.GET.dict(), "apiKey": self.api_key}
            headers = {
                k: v
                for k, v in request.headers.items()
                if k.lower()
                not in [
                    "host",
                    "connection",
                    "content-length",
                    "authorization",
                    "x-request-token",
                ]
            }

            user_info = "anonymous"
            if hasattr(request, "user") and request.user.is_authenticated:
                user_info = getattr(request.user, "email", str(request.user))

            logger.info(
                f"Forwarding {request.method} request to: {target_url} by user: {user_info}"
            )
            logger.info(f"With params: {params}")

            response = self.session.request(
                method=request.method,
                url=target_url,
                params=params,
                headers=headers,
                json=(
                    request.data if request.method in ["POST", "PUT", "PATCH"] else None
                ),
                timeout=self.timeout,
            )

            logger.info(f"Response status code: {response.status_code}")

            return self._process_response(response, request)
        except requests.Timeout:
            return self._error_response(
                "Gateway Timeout",
                "The request to Polygon.io timed out",
                status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except requests.RequestException as e:
            return self._error_response(
                "Bad Gateway", str(e), status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return self._error_response(
                "Internal Server Error", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _process_response(self, response, request):
        try:
            data = response.json() if response.content else {}

            if data:
                data = self._replace_polygon_urls(data, request)
                
                if "status" in data:
                    del data["status"]

            return Response(data=data, status=response.status_code)
        except ValueError:
            if response.status_code == 404:
                return self._error_response(
                    "Not Found",
                    "The requested resource was not found",
                    status.HTTP_404_NOT_FOUND,
                )
            return Response(
                data={"error": "Invalid JSON response", "content": response.text},
                status=response.status_code,
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
