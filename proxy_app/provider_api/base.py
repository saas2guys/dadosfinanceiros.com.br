from __future__ import annotations

from enum import Enum
import re
from typing import Any, Dict, Optional
from typing import Iterable, List, Sequence, Tuple

import httpx
from django.conf import settings
from django.urls import path
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class ProviderAPIView(APIView):

    endpoint_from: str = ""
    endpoint_to: str = ""
    name: str = ""
    allowed_params: Enum | None = None
    timeout: float = 20.0
    active: bool = True
    param_aliases: dict[str, str] = {}
    extra_query_params: dict[str, str] = {}
    query_serializer_class = None
    pagination_class = None
    paginate_locally: bool = False
    results_key: Optional[str] = "results"

    @classmethod
    def as_path(cls):
        if not cls.endpoint_from:
            raise RuntimeError(f"{cls.__name__} missing endpoint_from")
        raw = cls.endpoint_from
        if isinstance(raw, Enum):
            raw = raw.value
        route = str(raw).lstrip("/")
        route = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", r"<str:\1>", route)
        name = cls.name or cls.__name__.removesuffix("View").lower()
        return path(route, cls.as_view(), name=name)

    def build_params(self, request) -> Sequence[Tuple[str, str]] | dict:
        qp = request.query_params
        if self.query_serializer_class:
            serializer = self.query_serializer_class(data=qp)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                return {"__error__": {"detail": "invalid query params", "errors": e.detail}}
            validated = serializer.validated_data
            pairs: List[Tuple[str, str]] = []
            for k, v in validated.items():
                key = self.param_aliases.get(k, k)
                if isinstance(v, list):
                    for item in v:
                        pairs.append((key, str(item)))
                    continue
                pairs.append((key, str(v)))
            return pairs

        pairs: List[Tuple[str, str]] = []
        for k in qp.keys():
            key = self.param_aliases.get(k, k)
            for v in qp.getlist(k):
                pairs.append((key, v))
        return pairs

    def request(self, method: str, url: str, *, params: Iterable[Tuple[str, str]] | None = None) -> httpx.Response:
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        if not self.active:
            return Response({"detail": "endpoint disabled"}, status=status.HTTP_404_NOT_FOUND)
        if not self.endpoint_to:
            return Response({"detail": "endpoint_to not set"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        params = self.build_params(request)
        if isinstance(params, dict) and "__error__" in params:
            return Response(params["__error__"], status=status.HTTP_400_BAD_REQUEST)

        to_raw = self.endpoint_to
        if isinstance(to_raw, Enum):
            to_raw = to_raw.value
        to_path = str(to_raw)
        placeholders = set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", to_path))
        format_values: dict[str, str] = {}
        for ph in placeholders:
            if ph in kwargs:
                format_values[ph] = str(kwargs[ph])
                continue
            if ph in request.query_params:
                format_values[ph] = request.query_params.get(ph)  # type: ignore[assignment]
                continue
            return Response({"detail": "missing required parameter for provider path", "param": ph}, status=status.HTTP_400_BAD_REQUEST)

        formatted_to = to_path.format(**format_values) if placeholders else to_path

        pairs = list(params or [])  # type: ignore[arg-type]
        for key, value in kwargs.items():
            if key not in placeholders:
                pairs.append((key, str(value)))

        if self.param_aliases:
            pairs = [(self.param_aliases.get(k, k), v) for k, v in pairs]

        for k, v in self.extra_query_params.items():
            pairs.append((k, v))

        try:
            resp = self.request("GET", formatted_to, params=pairs)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            return Response({"detail": "upstream error", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        content_type = resp.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            try:
                data = resp.json()
            except ValueError:
                data = resp.text
            return self._maybe_paginate(data, request, resp.status_code)

        return Response(resp.text, status=resp.status_code)

    def _maybe_paginate(self, data: Any, request, status_code: int) -> Response:
        if not self.paginate_locally or self.pagination_class is None:
            return Response(data, status=status_code)

        items = None
        container: Optional[dict] = None
        if isinstance(data, dict) and self.results_key and self.results_key in data and isinstance(data[self.results_key], list):
            container = data
            items = data.get(self.results_key, [])
        elif isinstance(data, list):
            items = data
        if not isinstance(items, list):
            return Response(data, status=status_code)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(items, request, view=self)
        paginated_response = paginator.get_paginated_response(page)
        if container is None or not self.results_key:
            return paginated_response

        payload = paginated_response.data
        preserved = {k: v for k, v in container.items() if k != self.results_key}
        payload.update(preserved)
        return Response(payload, status=status_code)


class FMPBaseView(ProviderAPIView):
    base_url = getattr(settings, "FMP_BASE_URL", "https://financialmodelingprep.com")
    api_key_param = getattr(settings, "FMP_API_KEY_PARAM", "apikey")
    api_key_value = getattr(settings, "FMP_API_KEY", "")

    def request(self, method: str, url: str, *, params: Iterable[Tuple[str, str]] | None = None) -> httpx.Response:
        full_url = f"{self.base_url.rstrip('/')}{url}"
        pairs: List[Tuple[str, str]] = list(params or [])
        if self.api_key_value:
            pairs.append((self.api_key_param, self.api_key_value))
        return httpx.request(method, full_url, params=pairs, timeout=self.timeout)


class PolygonBaseView(ProviderAPIView):
    base_url = getattr(settings, "POLYGON_BASE_URL", "https://api.polygon.io")
    api_key_header = getattr(settings, "POLYGON_API_KEY_HEADER", "Authorization")
    api_key_value = getattr(settings, "POLYGON_API_KEY", "")

    def _headers(self) -> dict:
        if not self.api_key_value:
            return {}
        if self.api_key_header.lower() == "authorization":
            return {"Authorization": f"Bearer {self.api_key_value}"}
        return {self.api_key_header: self.api_key_value}

    def request(self, method: str, url: str, *, params: Iterable[Tuple[str, str]] | None = None) -> httpx.Response:
        full_url = f"{self.base_url.rstrip('/')}{url}"
        return httpx.request(method, full_url, params=list(params or []), headers=self._headers(), timeout=self.timeout)


