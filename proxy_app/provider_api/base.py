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


class ProviderAPIView(APIView):

    endpoint_from: str = ""
    endpoint_to: str = ""
    name: str = ""
    allowed_params: Enum | None = None
    strict_unknown: bool = False
    timeout: float = 20.0
    active: bool = True
    param_aliases: dict[str, str] = {}
    extra_query_params: dict[str, str] = {}
    shared_param_specs: Dict[str, Dict[str, Any]] = {}
    param_specs: Dict[str, Dict[str, Any]] = {}
    strict_types: bool = False
    drop_blank_values: bool = True
    # authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
    # permission_classes = [IsAuthenticated, DailyLimitPermission]
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
        incoming_keys = list(qp.keys())
        # Merge shared (provider-level) and view-level specs (view overrides shared)
        merged_specs: Dict[str, Dict[str, Any]] = {}
        if self.shared_param_specs:
            merged_specs.update(self.shared_param_specs)
        if self.param_specs:
            merged_specs.update(self.param_specs)

        spec_keys = set(merged_specs.keys()) if merged_specs else set()
        enum_keys = {p.value for p in self.allowed_params} if self.allowed_params else set()
        allowed_names = enum_keys | spec_keys or set(incoming_keys)

        if self.strict_unknown:
            unknown = sorted({k for k in incoming_keys if k not in allowed_names})
            if unknown:
                return {"__error__": {"detail": "unknown query params", "unknown": unknown}}

        errors: List[Dict[str, Any]] = []
        pairs: List[Tuple[str, str]] = []

        def is_blank(value: Any) -> bool:
            return value is None or (isinstance(value, str) and not value.strip())

        def coerce_bool(value: str) -> Optional[bool]:
            lower = value.strip().lower()
            if lower in {"1", "true", "t", "yes", "y"}:
                return True
            if lower in {"0", "false", "f", "no", "n"}:
                return False
            return None

        def coerce_value(value: str, type_name: str) -> Optional[Any]:
            if type_name == "int":
                try:
                    return int(value)
                except Exception:
                    return None
            if type_name == "float":
                try:
                    return float(value)
                except Exception:
                    return None
            if type_name == "bool":
                return coerce_bool(value)
            return str(value)

        processed_keys = set()
        for key in incoming_keys:
            if key not in allowed_names:
                continue
            processed_keys.add(key)
            spec = merged_specs.get(key, {}) if merged_specs else {}
            dest = spec.get("dest", key)
            type_name = spec.get("type", "str")
            separator = spec.get("separator", ",") if type_name == "csv" else None
            choices = set(spec.get("choices", [])) if spec.get("choices") else None
            min_v = spec.get("min")
            max_v = spec.get("max")

            raw_values: List[str] = []
            for rv in qp.getlist(key):
                if separator and rv:
                    raw_values.extend(rv.split(separator))
                    continue
                raw_values.append(rv)

            for raw in raw_values:
                if self.drop_blank_values and is_blank(raw):
                    continue
                coerced = coerce_value(raw, type_name)
                if coerced is None:
                    if self.strict_types:
                        errors.append({"param": key, "value": raw, "error": f"invalid {type_name}"})
                    continue

                if choices and str(coerced) not in {str(c) for c in choices}:
                    if self.strict_types:
                        errors.append({"param": key, "value": raw, "error": "not in allowed choices"})
                    continue

                if isinstance(coerced, (int, float)) and min_v is not None and coerced < min_v:
                    if self.strict_types:
                        errors.append({"param": key, "value": raw, "error": f"min {min_v}"})
                    continue

                if isinstance(coerced, (int, float)) and max_v is not None and coerced > max_v:
                    if self.strict_types:
                        errors.append({"param": key, "value": raw, "error": f"max {max_v}"})
                    continue

                pairs.append((dest, str(coerced)))

        for key, spec in (merged_specs or {}).items():
            if key in processed_keys or key not in allowed_names or "default" not in spec:
                continue
            dest = spec.get("dest", key)
            pairs.append((dest, str(spec["default"])))

        if errors:
            return {"__error__": {"detail": "invalid query params", "errors": errors}}
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
    shared_param_specs = {
        "limit": {"type": "int", "min": 1, "max": 1000, "dest": "limit"},
        "page": {"type": "int", "min": 1, "dest": "page"},
        "from": {"type": "str", "dest": "from"},
        "to": {"type": "str", "dest": "to"},
        "symbols": {"type": "csv", "separator": ",", "dest": "symbols"},
        "market": {"type": "str"},
        "sector": {"type": "str"},
        "exchange": {"type": "str"},
    }

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
    shared_param_specs = {
        "limit": {"type": "int", "min": 1, "max": 50000, "dest": "limit"},
        "offset": {"type": "int", "min": 0, "dest": "offset"},
        "multiplier": {"type": "int", "min": 1, "dest": "multiplier"},
        "timespan": {"type": "str", "dest": "timespan"},
        "from": {"type": "str", "dest": "from"},
        "to": {"type": "str", "dest": "to"},
        "symbols": {"type": "csv", "separator": ",", "dest": "tickers"},
    }

    def _headers(self) -> dict:
        if not self.api_key_value:
            return {}
        if self.api_key_header.lower() == "authorization":
            return {"Authorization": f"Bearer {self.api_key_value}"}
        return {self.api_key_header: self.api_key_value}

    def request(self, method: str, url: str, *, params: Iterable[Tuple[str, str]] | None = None) -> httpx.Response:
        full_url = f"{self.base_url.rstrip('/')}{url}"
        return httpx.request(method, full_url, params=list(params or []), headers=self._headers(), timeout=self.timeout)


