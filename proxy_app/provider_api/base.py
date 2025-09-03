from __future__ import annotations

from enum import Enum
import re
from typing import Optional

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


class ProviderAPIView(GenericAPIView):

    active: bool = True
    allowed_params: Enum | None = None
    endpoint_from: str = ""
    endpoint_to: str = ""
    pagination_class = None
    results_key: Optional[str] = "results"

    timeout: float = 20.0

    # class AnyParamsSerializer(serializers.Serializer):
    #     def to_internal_value(self, data):  # type: ignore[override]
    #         # Accept any incoming query params; preserve multi-values as lists
    #         items: dict[str, Any] = {}
    #         getlist = getattr(data, "getlist", None)
    #         keys = data.keys() if hasattr(data, "keys") else []
    #         for key in keys:
    #             if callable(getlist):
    #                 values = getlist(key)
    #             else:
    #                 raw = data.get(key)
    #                 values = raw if isinstance(raw, list) else [raw]
    #             if not values:
    #                 continue
    #             if len(values) == 1:
    #                 items[key] = values[0]
    #             else:
    #                 items[key] = values
    #         return items

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
        name = cls.name or cls.__name__.removesuffix("View").lower()
        return path(route, cls.as_view(), name=name)

    # ---- Request param handling ----
    def build_params(self, request) -> list[tuple[str, str]] | dict:
        qp = request.query_params
        if self.serializer_class:
            serializer = self.serializer_class(data=qp)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                return {
                    "__error__": {"detail": "invalid query params", "errors": e.detail}
                }
            validated = serializer.validated_data
            pairs: list[tuple[str, str]] = []
            for k, v in validated.items():
                if isinstance(v, list):
                    for item in v:
                        pairs.append((k, str(item)))
                    continue
                pairs.append((k, str(v)))
            return pairs

        pairs: list[tuple[str, str]] = []
        allowed_keys: set[str] | None = None
        if self.allowed_params is not None:
            # allowed_params is expected to be an Enum class containing allowed param names as values
            try:
                allowed_keys = {member.value for member in self.allowed_params}  # type: ignore[attr-defined]
            except Exception:
                allowed_keys = None

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
        resp = self.request("GET", url, params=params)
        resp.raise_for_status()
        return resp

    # ---- Response parsing ----
    def _parse_response(self, resp: httpx.Response):
        content_type = resp.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            try:
                return resp.json(), resp.status_code
            except ValueError:
                return resp.text, resp.status_code
        return resp.text, resp.status_code

    def request(
        self, method: str, url: str, *, params: list[tuple[str, str]] | None = None
    ) -> httpx.Response:
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
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
    api_key_param = getattr(settings, "FMP_API_KEY_PARAM", "apikey")
    api_key_value = getattr(settings, "FMP_API_KEY", "")

    class FMPSerializer(serializers.Serializer): ...

    serializer_class = FMPSerializer

    def request(
        self, method: str, url: str, *, params: list[tuple[str, str]] | None = None
    ) -> httpx.Response:
        full_url = f"{self.base_url.rstrip('/')}{url}"
        pairs: list[tuple[str, str]] = list(params or [])
        if self.api_key_value:
            pairs.append((self.api_key_param, self.api_key_value))
        return httpx.request(method, full_url, params=pairs, timeout=self.timeout)


class PolygonBaseView(ProviderAPIView):
    base_url = getattr(settings, "POLYGON_BASE_URL", "https://api.polygon.io")
    api_key_header = getattr(settings, "POLYGON_API_KEY_HEADER", "Authorization")
    api_key_value = getattr(settings, "POLYGON_API_KEY", "")
    serializer_class = ProviderAPIView.AnyParamsSerializer

    def _headers(self) -> dict:
        if not self.api_key_value:
            return {}
        if self.api_key_header.lower() == "authorization":
            return {"Authorization": f"Bearer {self.api_key_value}"}
        return {self.api_key_header: self.api_key_value}

    def request(
        self, method: str, url: str, *, params: list[tuple[str, str]] | None = None
    ) -> httpx.Response:
        full_url = f"{self.base_url.rstrip('/')}{url}"
        return httpx.request(
            method,
            full_url,
            params=list(params or []),
            headers=self._headers(),
            timeout=self.timeout,
        )
