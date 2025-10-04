import logging
import re
from enum import Enum
from typing import Any, Iterable, Optional, Protocol, Tuple

import httpx
from django.conf import settings
from django.urls import path
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .config import ProviderConfig
from .serializers import FMPResponseSerializer, PolygonResponseSerializer
from .strategies.endpoint import CurlyPlaceholderFormatter
from .strategies.params import SerializerParamBuilder
from .strategies.parsers import JsonOrTextParser
from .strategies.upstream import HttpxClient

logger = logging.getLogger(__name__)


class ParamBuilderStrategy(Protocol):
    """Strategy interface for building upstream query parameters.

    Implementations decide how to validate, filter, and flatten incoming
    query parameters into a list of ``(key, value)`` pairs suitable for HTTP
    requests. They may return an error envelope when validation fails.
    """

    def build(self, view: "ProviderAPIView", request) -> list[tuple[str, str]] | dict:
        """Build upstream query parameters for the given view and request.

        Args:
            view: The DRF view instance providing configuration (e.g.,
                ``allowed_params`` and ``serializer_class``).
            request: The current DRF request containing query parameters.

        Returns:
            A list of ``(key, value)`` pairs, or an error envelope of the form
            ``{"__error__": {...}}`` to be surfaced as a 400 response.
        """
        ...


class EndpointFormatterStrategy(Protocol):
    """Strategy interface for formatting provider-relative paths.

    Implementations replace placeholders in the path template using URL
    kwargs and/or query parameters and may return an error response if a
    required placeholder is missing.
    """

    def format(self, view: "ProviderAPIView", request, kwargs: dict) -> tuple[str, Optional[Response]]:
        """Format the view's provider path.

        Args:
            view: The DRF view instance with ``endpoint_to``.
            request: The current DRF request.
            kwargs: URL keyword arguments used to resolve placeholders.

        Returns:
            Tuple of ``(formatted_path, error_response)`` where the error part
            is ``None`` on success or a DRF ``Response`` when a parameter is
            missing.
        """
        ...


class UpstreamClientStrategy(Protocol):
    """Strategy interface for executing upstream HTTP requests."""

    def request(
        self,
        view: "ProviderAPIView",
        method: str,
        url_path: str,
        *,
        params: Iterable[Tuple[str, str]] = (),
    ) -> httpx.Response:
        """Issue an HTTP request to the upstream provider.

        Args:
            view: The calling view instance; may supply timeout or other hints.
            method: HTTP method name (e.g., "GET").
            url_path: Provider-relative path (already formatted).
            params: Query-string pairs to include.

        Returns:
            The HTTPX response.
        """
        ...


class ResponseParserStrategy(Protocol):
    """Strategy interface for parsing upstream HTTP responses."""

    def parse(self, view: "ProviderAPIView", resp: httpx.Response) -> tuple[Any, int]:
        """Parse the upstream response and return a data/status tuple.

        Args:
            view: The calling view; may provide a ``response_serializer_class``.
            resp: The upstream HTTPX response to parse.

        Returns:
            Tuple of ``(data, status_code)`` where data is JSON-serializable or
            a text string when not JSON.
        """
        ...


class ProviderAPIView(GenericAPIView):
    """Base view that orchestrates provider proxy calls using injectable strategies.

    This class coordinates four main steps for read-only proxy endpoints:
    1) Build upstream query parameters (``param_builder``)
    2) Format the provider path (``endpoint_formatter``)
    3) Execute the upstream HTTP request (``upstream_client``)
    4) Parse and serialize the upstream response (``response_parser``)

    It also optionally applies pagination using DRF's paginator when the
    serialized payload is a list or a dict that contains a list under
    ``results_key``.

    Attributes:
        active: When False, the endpoint returns a 404 immediately.
        allowed_params: Enum or iterable of Enums/strings defining allowed
            query parameter names.
        endpoint_from: Public route template used to generate Django ``path``.
        endpoint_to: Provider-relative path template that may include
            ``{placeholders}`` filled by kwargs or query params.
        results_key: Key name in dict payloads that holds a list to paginate.
        timeout: Default timeout used by upstream clients (seconds).
        serializer_class: Optional DRF serializer for validating query params.
        param_builder: Strategy to build query params for upstream.
        endpoint_formatter: Strategy to format provider path.
        upstream_client: Strategy to perform upstream HTTP request.
        response_parser: Strategy to parse and serialize upstream response.
    """

    active: bool = True
    allowed_params: Enum | None = None
    endpoint_from: Enum | None = None
    endpoint_to: Enum | None = None
    results_key: Optional[str] = "results"

    timeout: float = 20.0

    http_method_names = ["get"]

    serializer_class = None

    # Optional strategy injection points (default to None → use built-in behavior)
    param_builder: ParamBuilderStrategy | None = None
    endpoint_formatter: EndpointFormatterStrategy | None = None
    upstream_client: UpstreamClientStrategy | None = None
    response_parser: ResponseParserStrategy | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.param_builder is None:
            self.param_builder = SerializerParamBuilder()
        if self.endpoint_formatter is None:
            self.endpoint_formatter = CurlyPlaceholderFormatter()
        if self.response_parser is None:
            self.response_parser = JsonOrTextParser()

    @classmethod
    def as_path(cls):
        """Return a Django ``path`` object for the view's public route.

        Converts ``{placeholders}`` in ``endpoint_from`` into Django path
        converters of the form ``<str:name>`` and derives a default route name
        from the class name (lowercased without the ``View`` suffix) unless a
        ``name`` attribute is present.

        Raises:
            RuntimeError: If ``endpoint_from`` is not defined on the class.
        """
        if not cls.endpoint_from:
            raise RuntimeError(f"{cls.__name__} missing endpoint_from")
        raw = cls.endpoint_from.value if isinstance(cls.endpoint_from, Enum) else cls.endpoint_from
        route = str(raw).lstrip("/")
        route = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", r"<str:\1>", route)
        name = getattr(cls, "name", None) or cls.__name__.removesuffix("View").lower()
        return path(route, cls.as_view(), name=name)

    # ---- Request param handling ----
    def build_params(self, request) -> list[tuple[str, str]] | dict:
        """Build and validate upstream query parameters.

        Delegates to the configured ``param_builder``. When a
        ``serializer_class`` is defined on the view, the default param builder
        will validate query params using the serializer and flatten the
        resulting mapping into a list of ``(key, value)`` pairs. Allowed
        parameters filtering is applied via ``allowed_params``.

        Args:
            request: DRF request instance holding query parameters.

        Returns:
            A list of ``(key, value)`` pairs suitable for HTTP query strings,
            or an error envelope ``{"__error__": {...}}`` when validation
            fails.
        """
        if self.param_builder is None:
            self.param_builder = SerializerParamBuilder()
        return self.param_builder.build(self, request)

    # ---- URL formatting ----
    def _format_endpoint_to(self, request, kwargs: dict) -> tuple[str, Optional[Response]]:
        """Format the provider-relative path from ``endpoint_to``.

        Fills ``{placeholders}`` from URL kwargs, then falls back to query
        parameters. Returns an error response if any required placeholder is
        missing.

        Args:
            request: DRF request instance.
            kwargs: URL keyword arguments.

        Returns:
            Tuple of ``(formatted_path, error_response)`` where
            ``error_response`` is ``None`` on success or a DRF ``Response``
            with status 400 when a required placeholder is missing.
        """
        if self.endpoint_formatter is None:
            self.endpoint_formatter = CurlyPlaceholderFormatter()
        return self.endpoint_formatter.format(self, request, kwargs)

    # ---- Upstream call ----
    def _perform_upstream(self, url: str, params: list[tuple[str, str]]):
        """Perform the upstream HTTP request.

        Uses the injected ``upstream_client`` if present; otherwise calls the
        subclass-provided ``perform_request`` and ensures
        ``raise_for_status()`` is invoked.

        Args:
            url: Provider-relative path to request.
            params: Query-string pairs to include.

        Returns:
            The HTTPX response.
        """
        # Delegate if a strategy is provided
        if self.upstream_client is not None:
            resp = self.upstream_client.request(self, "GET", url, params=params)
            return resp
        resp = self.perform_request("GET", url, params=params)
        resp.raise_for_status()
        return resp

    # ---- Response parsing ----
    def _parse_response(self, resp: httpx.Response):
        """Parse the upstream response using the configured strategy.

        The default strategy returns JSON-serialized data when the content type
        indicates JSON, delegating to ``response_serializer_class`` for
        representation. Otherwise, it returns the raw text body.

        Args:
            resp: HTTPX response from the upstream provider.

        Returns:
            Tuple ``(data, status_code)`` where data is a JSON-serializable
            structure or a text string.
        """
        if self.response_parser is None:
            self.response_parser = JsonOrTextParser()
        return self.response_parser.parse(self, resp)

    def _get_used_placeholders(self, formatted_to: str) -> set[str]:
        """Extract placeholder names used in a formatted provider path.

        Args:
            formatted_to: Provider path that may contain ``{placeholders}``.

        Returns:
            A set of placeholder names present in ``formatted_to``.
        """
        return set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", formatted_to))

    def _append_non_path_kwargs(self, formatted_to: str, kwargs: dict, pairs: list[tuple[str, str]]):
        """Append non-placeholder kwargs as query parameters.

        Args:
            formatted_to: Provider path used to detect consumed placeholders.
            kwargs: URL keyword arguments.
            pairs: Mutable list of query param pairs to be extended.
        """
        used = self._get_used_placeholders(formatted_to)
        for key, value in kwargs.items():
            if key in used:
                continue
            pairs.append((key, str(value)))

    def _paginate_if_needed(self, data: Any, status_code: int) -> Response | None:
        """Paginate a collection when pagination is configured and applicable.

        Args:
            data: Parsed response payload (list or dict).
            status_code: Original upstream status code to preserve.

        Returns:
            A paginated DRF ``Response`` or ``None`` if pagination does not
            apply.
        """
        page = self.paginate_queryset(data)
        if page is None:
            return None
        paginated = self.get_paginated_response(page)
        paginated.status_code = status_code
        return paginated

    def perform_request(self, method: str, url: str, *, params: Iterable[Tuple[str, str]] = ()) -> httpx.Response:
        """Perform a synchronous HTTP request to the provider.

        Subclasses that do not supply an ``upstream_client`` must implement
        this method to execute the HTTP request.

        Args:
            method: HTTP method name (e.g., "GET").
            url: Provider-relative path beginning with ``/``.
            params: Query-string pairs to include.

        Returns:
            An HTTPX response.
        """
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        """Handle GET requests by proxying to the configured upstream provider.

        This method follows an early-return style to keep branching shallow.
        It also sets ``self.request`` to the incoming request to ensure DRF's
        pagination helpers work when ``get()`` is invoked directly in tests.

        Flow:
          1) Validate endpoint configuration and parameters
          2) Format provider path and merge non-path kwargs into query params
          3) Perform upstream call and parse response
          4) Optionally paginate lists or dicts containing ``results_key``

        Returns:
            A DRF ``Response`` containing serialized data from the upstream
            provider (possibly paginated) and the upstream status code.
        """
        logger.debug(f"DEBUG: GET method called for {self.__class__.__name__}")
        # Ensure DRF pagination helpers have access to the request even when
        # tests call get() directly instead of dispatching via as_view().
        # DRF normally sets self.request in dispatch; we mirror that here.
        try:
            self.request = request  # type: ignore[assignment]
        except Exception:
            pass
        if not self.active:
            return Response({"detail": "endpoint disabled"}, status=status.HTTP_404_NOT_FOUND)
        if not self.endpoint_to:
            return Response({"detail": "endpoint_to not set"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        params = self.build_params(request)
        if isinstance(params, dict) and "__error__" in params:
            return Response(params["__error__"], status=status.HTTP_400_BAD_REQUEST)

        formatted_to, error = self._format_endpoint_to(request, kwargs)
        if error is not None:
            return error

        pairs = list(params)  # type: ignore[arg-type]
        self._append_non_path_kwargs(formatted_to, kwargs, pairs)

        try:
            resp = self._perform_upstream(formatted_to, pairs)
        except httpx.HTTPError as e:
            return Response({"detail": "upstream error", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        data, status_code = self._parse_response(resp)
        logger.debug(f"DEBUG: Status Code: {status_code}, Class: {self.__class__.__name__}")

        # If view-level pagination is configured, paginate lists or dicts with results_key
        if isinstance(data, list):
            page = self.paginate_queryset(data)
            if page is not None:
                paginated = self.get_paginated_response(page)
                paginated.status_code = status_code
                return paginated

        if isinstance(data, dict) and self.results_key and self.results_key in data and isinstance(data[self.results_key], list):
            items = data[self.results_key]
            page = self.paginate_queryset(items)
            if page is not None:
                paginated = self.get_paginated_response(page)
                payload = dict(paginated.data)
                preserved = {k: v for k, v in data.items() if k != self.results_key}
                payload.update(preserved)
                return Response(payload, status=status_code)

        return Response(data, status=status_code)


class FMPBaseView(ProviderAPIView):
    """Base view for FMP endpoints.

    Provides ``response_serializer_class`` and configures a default
    ``HttpxClient`` using Django settings.
    """

    response_serializer_class = FMPResponseSerializer
    upstream_client = HttpxClient(
        ProviderConfig(
            base_url=settings.FMP_BASE_URL,
            api_key_param="apikey",
            api_key_value=settings.FMP_API_KEY,
            timeout=settings.PROXY_TIMEOUT,
        )
    )


class PolygonBaseView(ProviderAPIView):
    """Base view for Polygon endpoints.

    Provides ``response_serializer_class`` and configures a default
    ``HttpxClient`` using Django settings.
    """

    response_serializer_class = PolygonResponseSerializer
    upstream_client = HttpxClient(
        ProviderConfig(
            base_url=settings.POLYGON_BASE_URL,
            api_key_param="apikey",
            api_key_value=settings.POLYGON_API_KEY,
            timeout=settings.PROXY_TIMEOUT,
        )
    )
