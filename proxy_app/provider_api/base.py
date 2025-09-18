from __future__ import annotations

from enum import Enum
import re
import logging
from typing import Optional, Any
from urllib.parse import urlparse, urljoin

import httpx
from django.conf import settings
from django.urls import path
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission

from .serializers import ProviderResponseSerializer

logger = logging.getLogger(__name__)


class ProviderAPIView(GenericAPIView):

    active: bool = True
    allowed_params: Enum | None = None
    endpoint_from: Enum | None = None
    endpoint_to: Enum | None = None
    pagination_class = None
    results_key: Optional[str] = "results"

    timeout: float = 20.0

    class AnyParamsSerializer(serializers.Serializer):
        def to_internal_value(self, data):  # type: ignore[override]
            # Accept any incoming query params; preserve multi-values as lists
            items: dict[str, Any] = {}
            getlist = getattr(data, "getlist", None)
            keys = data.keys() if hasattr(data, "keys") else []
            for key in keys:
                if callable(getlist):
                    values = getlist(key)
                else:
                    raw = data.get(key)
                    values = raw if isinstance(raw, list) else [raw]
                if not values:
                    continue
                if len(values) == 1:
                    items[key] = values[0]
                else:
                    items[key] = values
            return items

    serializer_class = None
    authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
    permission_classes = [IsAuthenticated, DailyLimitPermission, AllowAny]

    @classmethod
    def as_path(cls):
        if not cls.endpoint_from:
            raise RuntimeError(f"{cls.__name__} missing endpoint_from")
        raw = cls.endpoint_from
        if isinstance(raw, Enum):
            raw = raw.value
        route = str(raw).lstrip("/")
        route = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", r"<str:\1>", route)
        name = getattr(cls, "name", None) or cls.__name__.removesuffix("View").lower()
        return path(route, cls.as_view(), name=name)

    # ---- Request param handling ----
    def build_params(self, request) -> list[tuple[str, str]] | dict:
        qp = request.query_params
        def _collect_allowed_keys(spec) -> set[str] | None:
            if spec is None:
                return None
            try:
                # Single Enum class
                return {member.value for member in spec}  # type: ignore[arg-type]
            except Exception:
                pass
            try:
                # Iterable of Enum classes
                keys: set[str] = set()
                for enum_cls in (spec if isinstance(spec, (list, tuple, set)) else []):
                    try:
                        keys.update({member.value for member in enum_cls})  # type: ignore[arg-type]
                    except Exception:
                        continue
                return keys or None
            except Exception:
                return None
        if self.serializer_class:
            serializer = self.serializer_class(data=qp)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                return {
                    "__error__": {"detail": "invalid query params", "errors": e.detail}
                }
            validated = serializer.validated_data
            # If allowed_params is set, filter the validated params accordingly
            allowed_keys = _collect_allowed_keys(self.allowed_params)
            pairs: list[tuple[str, str]] = []
            for k, v in validated.items():
                if allowed_keys is not None and k not in allowed_keys:
                    continue
                if isinstance(v, list):
                    for item in v:
                        pairs.append((k, str(item)))
                    continue
                pairs.append((k, str(v)))
            return pairs

        pairs: list[tuple[str, str]] = []
        allowed_keys = _collect_allowed_keys(self.allowed_params)

        for k in qp.keys():
            if allowed_keys is not None and k not in allowed_keys:
                continue
            for v in qp.getlist(k):
                pairs.append((k, v))
        return pairs

    # ---- URL formatting ----
    def _format_endpoint_to(
        self, request, kwargs: dict
    ) -> tuple[str, Optional[Response]]:
        to_raw = self.endpoint_to
        if isinstance(to_raw, Enum):
            to_raw = to_raw.value
        to_path = str(to_raw)
        placeholders = set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", to_path))
        if not placeholders:
            return to_path, None
        values: dict[str, str] = {}
        for ph in placeholders:
            if ph in kwargs:
                values[ph] = str(kwargs[ph])
                continue
            if ph in request.query_params:
                values[ph] = request.query_params.get(ph)  # type: ignore[assignment]
                continue
            return "", Response(
                {"detail": "missing required parameter for provider path", "param": ph},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return to_path.format(**values), None

    # ---- Upstream call ----
    def _perform_upstream(self, url: str, params: list[tuple[str, str]]):
        resp = self.perform_request("GET", url, params=params)
        resp.raise_for_status()
        return resp

    # ---- Response parsing ----
    def _parse_response(self, resp: httpx.Response):
        content_type = resp.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            try:
                data = resp.json()
                if hasattr(self, 'response_serializer') and self.response_serializer:
                    data = self.response_serializer.to_representation(data)
                return data, resp.status_code
            except ValueError:
                return resp.text, resp.status_code
        return resp.text, resp.status_code

    def perform_request(
        self, method: str, url: str, *, params: list[tuple[str, str]] | None = None
    ) -> httpx.Response:
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        logger.debug(f"DEBUG: GET method called for {self.__class__.__name__}")
        if not self.active:
            return Response(
                {"detail": "endpoint disabled"}, status=status.HTTP_404_NOT_FOUND
            )
        if not self.endpoint_to:
            return Response(
                {"detail": "endpoint_to not set"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        params = self.build_params(request)
        if isinstance(params, dict) and "__error__" in params:
            return Response(params["__error__"], status=status.HTTP_400_BAD_REQUEST)

        formatted_to, error = self._format_endpoint_to(request, kwargs)
        if error is not None:
            return error

        pairs = list(params or [])  # type: ignore[arg-type]
        # include any non-path kwargs as query params
        used = set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", formatted_to))
        for key, value in kwargs.items():
            if key not in used:
                pairs.append((key, str(value)))

        try:
            resp = self._perform_upstream(formatted_to, pairs)
        except httpx.HTTPError as e:
            return Response(
                {"detail": "upstream error", "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data, status_code = self._parse_response(resp)
        logger.debug(f"DEBUG: Status Code: {status_code}, Class: {self.__class__.__name__}")  # Log do status code para debug
        if self.pagination_class is None:
            return Response(data, status=status_code)

        # Use DRF GenericAPIView helpers for pagination
        if isinstance(data, list):
            page = self.paginate_queryset(data)
            if page is not None:
                paginated = self.get_paginated_response(page)
                paginated.status_code = status_code
                return paginated
            return Response(data, status=status_code)

        if (
            isinstance(data, dict)
            and self.results_key
            and self.results_key in data
            and isinstance(data[self.results_key], list)
        ):
            items = data[self.results_key]
            page = self.paginate_queryset(items)
            if page is not None:
                paginated = self.get_paginated_response(page)
                payload = dict(paginated.data)
                preserved = {k: v for k, v in data.items() if k != self.results_key}
                payload.update(preserved)
                response = Response(payload, status=status_code)
                return response
        return Response(data, status=status_code)


class FMPBaseView(ProviderAPIView):
    base_url = getattr(settings, "FMP_BASE_URL", "https://financialmodelingprep.com")
    api_key_value = getattr(settings, "FMP_API_KEY", "")
    api_key_param = "apikey"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_serializer = ProviderResponseSerializer(self.base_url, "fmp")

    def perform_request(
        self, method: str, url: str, *, params: list[tuple[str, str]] | None = None
    ) -> httpx.Response:
        full_url = f"{self.base_url.rstrip('/')}{url}"
        pairs: list[tuple[str, str]] = list(params or [])
        if self.api_key_value:
            pairs.append((self.api_key_param, self.api_key_value))
        return httpx.request(method, full_url, params=pairs, timeout=self.timeout)


class PolygonBaseView(ProviderAPIView):
    base_url = getattr(settings, "POLYGON_BASE_URL", "https://api.polygon.io")
    api_key_value = getattr(settings, "POLYGON_API_KEY", "")
    api_key_param = "apikey"

    serializer_class = ProviderAPIView.AnyParamsSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_serializer = ProviderResponseSerializer(self.base_url, "polygon")

    def perform_request(
        self, method: str, url: str, *, params: list[tuple[str, str]] | None = None
    ) -> httpx.Response:
        full_url = f"{self.base_url.rstrip('/')}{url}"
        pairs: list[tuple[str, str]] = list(params or [])
        if self.api_key_value:
            pairs.append((self.api_key_param, self.api_key_value))
        return httpx.request(method, full_url, params=pairs, timeout=self.timeout)