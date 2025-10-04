import types
from unittest.mock import MagicMock, patch

import httpx
from django.conf import settings
from django.test import TestCase
from django.urls.resolvers import URLPattern
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from proxy_app.provider_api.base import FMPBaseView, PolygonBaseView, ProviderAPIView
from proxy_app.provider_api.config import ProviderConfig
from proxy_app.provider_api.enums import (
    EndpointFrom,
    EndpointToFMP,
    EndpointToPolygon,
    PolygonParams,
)
from proxy_app.provider_api.exceptions import UpstreamAPIException
from proxy_app.provider_api.pagination import ResultsKeyPagination
from proxy_app.provider_api.serializers import ProviderResponseSerializer
from proxy_app.provider_api.strategies.endpoint import CurlyPlaceholderFormatter
from proxy_app.provider_api.strategies.params import SerializerParamBuilder
from proxy_app.provider_api.strategies.parsers import JsonOrTextParser
from proxy_app.provider_api.strategies.upstream import HttpxClient


def bind_perform_request(view, func):
    """Bind a fake upstream client that delegates to ``func``.

    The provided ``func`` should accept signature ``(self, method, url_path, *, params=None)``
    and return an ``httpx.Response``-like object. This mirrors the new UpstreamClientStrategy
    used by ProviderAPIView.
    """

    class UC:
        def request(self, _view, method, url_path, *, params=None):
            return func(_view, method, url_path, params=params)

    view.upstream_client = UC()


class ProviderAnyView(ProviderAPIView):
    """Minimal provider view used as a baseline in unit tests.

    Purpose:
        Exercise default parameter collection, endpoint formatting, and
        response parsing without any serializer- or enum-based filtering.

    Notes:
        - ``serializer_class`` is not set, so all query parameters are accepted.
        - ``allowed_params`` is not set, so no allowlist filtering is applied.
    """


class FilteredProviderView(ProviderAPIView):
    """View that exercises allowlist filtering via real Polygon enums.

    Purpose:
        Verify that only keys defined by the provided enums are forwarded, and
        unknown keys are ignored.

    Attributes:
        allowed_params: Set to commonly used Polygon parameter enums.
    """

    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTickers]


class AnyParamsSerializer(serializers.Serializer):
    """Permissive serializer for tests that accepts any query parameters.

    Purpose:
        Emulate a serializer that does not perform strict validation while
        preserving multi-value inputs (e.g., ``?a=1&a=2``) as lists before
        they are flattened by the param builder.

    Behavior:
        - Converts a QueryDict-like object into a mapping of keys to either a
          single value or a list of values when repeated.
    """

    def to_internal_value(self, data):  # type: ignore[override]
        items = {}
        getlist = getattr(data, "getlist", None)
        keys = data.keys() if hasattr(data, "keys") else []
        for key in keys:
            values = getlist(key) if callable(getlist) else data.get(key)
            values = values if isinstance(values, list) else [values]
            if not values:
                continue
            if len(values) == 1:
                items[key] = values[0]
            else:
                items[key] = values
        return items


class SerializerProviderView(ProviderAPIView):
    """View that combines a permissive serializer with an allowlist filter.

    Purpose:
        Validate that serializer-based normalization and enum-based parameter
        filtering compose correctly in the param builder.

    Attributes:
        serializer_class: Uses ``AnyParamsSerializer`` to accept inputs.
        allowed_params: Restricts forwarded keys to the specified enums.
    """

    serializer_class = AnyParamsSerializer
    allowed_params = [PolygonParams.Common, PolygonParams.ReferenceTickers]


class IterProviderView(ProviderAPIView):
    """View showcasing iterable ``allowed_params`` with a single enum.

    Purpose:
        Ensure that ``allowed_params`` supports an iterable of enums and still
        filters keys as expected.
    """

    allowed_params = [PolygonParams.Common]


class StrictSerializer(serializers.Serializer):
    """Strict serializer used to trigger validation errors during tests.

    Fields:
        required: A mandatory string field that must be present for the
            serializer to validate successfully.
    """

    required = serializers.CharField(required=True)


class StrictProviderView(ProviderAPIView):
    """View that uses a strict serializer to assert 400 error propagation.

    Purpose:
        Confirm the param builder returns an error envelope when DRF validation
        fails and that the view translates it into a 400 response.
    """

    serializer_class = StrictSerializer


class ProviderToEma(ProviderAPIView):
    """Helper view configured with a provider path template for EMA.

    Purpose:
        Test placeholder resolution behavior (kwargs vs query param precedence)
        and missing-parameter errors for Polygon EMA endpoints.
    """

    endpoint_to = EndpointToPolygon.INDICATOR_EMA


class InactiveProviderView(ProviderAPIView):
    """Helper view that is disabled to verify early 404 behavior.

    Purpose:
        Ensure the view returns a 404 without attempting upstream calls when
        ``active`` is set to ``False``.
    """

    active = False
    endpoint_from = EndpointFrom.STOCKS_REFERENCE_NEWS
    endpoint_to = EndpointToPolygon.REFERENCE_NEWS


class BadProviderView(ProviderAPIView):
    """Misconfigured view to validate 500 response when ``endpoint_to`` is missing.

    Purpose:
        Confirm that misconfiguration is detected and reported as a 500.
    """

    endpoint_from = EndpointFrom.STOCKS_REFERENCE_NEWS
    endpoint_to = None


class EmaFromView(ProviderAPIView):
    """Helper view to test route generation with placeholders.

    Purpose:
        Validate that ``as_path`` converts ``{placeholders}`` into Django path
        converters and derives an appropriate route name.
    """

    endpoint_from = EndpointFrom.STOCKS_INDICATOR_EMA


class EmaFromNamedView(ProviderAPIView):
    """Helper view with explicit route name for ``as_path`` tests.

    Purpose:
        Ensure that the ``name`` attribute overrides the default naming logic.
    """

    endpoint_from = EndpointFrom.STOCKS_INDICATOR_EMA
    name = "custom"


class PolygonEmaView(PolygonBaseView):
    """Concrete Polygon view for EMA endpoints used throughout tests.

    Purpose:
        Provide a realistic Polygon configuration for exercising formatting,
        param forwarding, response rewriting, and pagination behavior.
    """

    endpoint_from = EndpointFrom.STOCKS_INDICATOR_EMA
    endpoint_to = EndpointToPolygon.INDICATOR_EMA
    allowed_params = [PolygonParams.IndicatorCommon]


class PolygonAggView(PolygonBaseView):
    """Polygon view targeting aggregate custom range endpoints.

    Purpose:
        Exercise placeholder resolution across multiple variables (some from
        kwargs and others from query parameters) for complex provider paths.
    """

    endpoint_from = EndpointFrom.STOCKS_AGGREGATE_CUSTOM_RANGE
    endpoint_to = EndpointToPolygon.AGG_CUSTOM_RANGE


class FMPExecsView(FMPBaseView):
    """FMP view targeting a company executives endpoint for filtering tests.

    Purpose:
        Validate FMP serializer transformations (e.g., URL filtering) and
        standardization of list payloads under ``results``.
    """

    endpoint_from = EndpointFrom.COMPANY_EXECUTIVES
    endpoint_to = EndpointToFMP.COMPANY_EXECUTIVES


class FMPAnyView(FMPBaseView):
    """FMP view used to validate single-object standardization.

    Purpose:
        Ensure that a single dict payload is wrapped into a ``results`` list
        and enriched with processing metadata where applicable.
    """

    endpoint_from = EndpointFrom.COMPANY_EXECUTIVES
    endpoint_to = EndpointToFMP.COMPANY_EXECUTIVES


class ProviderAPIViewUnitTests(TestCase):
    """Test suite for `ProviderAPIView` orchestration, params, and routing.

    Covers `as_path`, parameter building with and without serializers, allowed
    parameter filtering, placeholder formatting, and overall GET flow
    including early returns and pagination delegation.
    """

    def setUp(self) -> None:
        """Prepare an APIRequestFactory for constructing DRF Request objects."""
        self.factory = APIRequestFactory()

    def test_as_path_replaces_placeholders_and_sets_name(self):
        """Verify as_path() converts {placeholders} to Django path converters and sets a default name.

        Approach: define a minimal view with endpoint_from containing a placeholder, call as_path(),
        and assert the route contains <str:...> and the generated name matches the class convention.
        Expected: route with <str:stockTicker>/ and name 'emaview'.
        """
        urlpattern: URLPattern = EmaFromView.as_path()

        self.assertEqual(str(urlpattern.pattern), "stocks/indicators/ema/<str:stockTicker>/")
        self.assertEqual(urlpattern.name, "emafrom")

    def test_build_params_no_serializer_collects_all_and_multivalues(self):
        """Ensure build_params collects all query params without validation and preserves multi-values.

        Approach: send 'a' as multi-valued and 'b' as single-valued; call build_params.
        Expected: two pairs for 'a' and one for 'b'.
        """
        view = ProviderAnyView()
        django_request = self.factory.get("/x", {"a": ["1", "2"], "b": "3"})
        request = Request(django_request)
        pairs = view.build_params(request)
        self.assertCountEqual(pairs, [("a", "1"), ("a", "2"), ("b", "3")])

    def test_build_params_with_allowed_params_filters_keys(self):
        """Verify allowed_params (using real PolygonParams enums) filters out unknown keys.

        Approach: set allowed_params to [PolygonParams.Common, PolygonParams.ReferenceTickers] and include
        an unknown key.
        Expected: only 'cursor' and 'search' are returned; 'unknown' is ignored.
        """
        view = FilteredProviderView()
        django_request = self.factory.get("/x", {"cursor": "abc", "search": "apple", "unknown": "x"})
        request = Request(django_request)
        pairs = view.build_params(request)
        self.assertIn(("cursor", "abc"), pairs)
        self.assertIn(("search", "apple"), pairs)
        self.assertNotIn(("unknown", "x"), pairs)

    def test_build_params_with_serializer_and_allowed_params(self):
        """Validate serializer-based input respects allowed_params and expands lists to pairs.

        Approach: use AnyParamsSerializer to accept anything, set allowed_params to
        [PolygonParams.Common, PolygonParams.ReferenceTickers], supply list values for 'cursor'.
        Expected: one pair per 'cursor' value; unrelated keys filtered out.
        """
        view = SerializerProviderView()
        django_request = self.factory.get("/x", {"cursor": ["a", "b"], "foo": "bar"})
        request = Request(django_request)
        pairs = view.build_params(request)
        self.assertCountEqual(pairs, [("cursor", "a"), ("cursor", "b")])

    def test_build_params_with_iterable_allowed_params(self):
        """Confirm iterable allowed_params (list of Enums) is supported and filters keys accordingly.

        Approach: set allowed_params to [PolygonParams.Common] and provide 'cursor' and 'other'.
        Expected: only 'cursor' is included in the resulting pairs.
        """
        view = IterProviderView()
        django_request = self.factory.get("/x", {"cursor": "abc", "other": "x"})
        request = Request(django_request)
        pairs = view.build_params(request)
        self.assertEqual(pairs, [("cursor", "abc")])

    def test_serializer_validation_error_returns_error_dict(self):
        """Ensure invalid serializer input leads to error dict with details from DRF ValidationError.

        Approach: use a strict serializer requiring 'required' field; omit it in query params.
        Expected: build_params returns a dict with '__error__' and a 400-friendly payload.
        """
        view = StrictProviderView()
        request = Request(self.factory.get("/x", {"optional": "ok"}))
        result = view.build_params(request)
        self.assertIsInstance(result, dict)
        self.assertIn("__error__", result)
        self.assertIn("errors", result["__error__"])

    def test_format_endpoint_to_missing_placeholder_returns_error(self):
        """Ensure missing required placeholders result in a 400 Response and empty path.

        Approach: endpoint_to requires {stockTicker}; call _format_endpoint_to without kwargs or query.
        Expected: path == "" and Response with status 400 and param name in payload.
        """
        view = ProviderToEma()
        request = Request(self.factory.get("/x"))
        path, error = view._format_endpoint_to(request, kwargs={})
        self.assertEqual(path, "")
        self.assertIsNotNone(error)
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.data.get("param"), "stockTicker")

    def test_format_endpoint_to_uses_kwargs_then_query_params(self):
        """Check placeholder value resolution prefers kwargs over query params when both exist.

        Approach: provide stockTicker in query and kwargs; call _format_endpoint_to.
        Expected: formatted path uses the kwargs value.
        """
        view = ProviderToEma()

        django_request = self.factory.get("/x", {"stockTicker": "AAPL"})
        request = Request(django_request)
        path, error = view._format_endpoint_to(request, kwargs={"stockTicker": "MSFT"})
        self.assertIsNone(error)
        self.assertIn("MSFT", path)

    def test_format_endpoint_to_uses_query_params_when_kwargs_missing(self):
        """Verify placeholders are satisfied from query params when kwargs are not provided.

        Approach: provide only query param for required placeholder; call _format_endpoint_to.
        Expected: formatted path uses query param value without error.
        """
        view = ProviderToEma()
        request = Request(self.factory.get("/x", {"stockTicker": "TSLA"}))
        path, error = view._format_endpoint_to(request, kwargs={})
        self.assertIsNone(error)
        self.assertIn("TSLA", path)

    def test_get_inactive_returns_404(self):
        """Verify GET returns 404 when view.active is False.

        Approach: define inactive view and call get() directly.
        Expected: Response with status 404 and no upstream interactions.
        """
        view = InactiveProviderView()
        response = view.get(Request(self.factory.get("/x")))
        self.assertEqual(response.status_code, 404)

    def test_get_missing_endpoint_to_returns_500(self):
        """Ensure GET returns 500 if endpoint_to is not configured on the view.

        Approach: omit endpoint_to and call get().
        Expected: Response with status 500.
        """
        view = BadProviderView()
        response = view.get(Request(self.factory.get("/x")))
        self.assertEqual(response.status_code, 500)

    def test_get_returns_400_when_placeholder_missing(self):
        """End-to-end GET should propagate _format_endpoint_to placeholder error as 400 response.

        Approach: endpoint_to requires {stockTicker}, but call get() without it.
        Expected: Response with status 400.
        """
        view = PolygonEmaView()
        resp = view.get(Request(self.factory.get("/x")))
        self.assertEqual(resp.status_code, 400)

    def test_as_path_custom_name_attribute(self):
        """Confirm as_path uses explicit 'name' attribute when provided on the view class.

        Approach: set name = 'custom'; call as_path.
        Expected: urlpattern.name == 'custom'.
        """

        class EMAView(ProviderAPIView):
            endpoint_from = EndpointFrom.STOCKS_INDICATOR_EMA
            name = "custom"

        urlpattern: URLPattern = EMAView.as_path()
        self.assertEqual(urlpattern.name, "custom")


class PolygonBaseViewUnitTests(TestCase):
    """Integration-style tests for `PolygonBaseView` GET behavior.

    Exercises param merging, response parsing, upstream error handling, and
    text passthrough behavior specific to Polygon endpoints.
    """

    def setUp(self) -> None:
        """Prepare an APIRequestFactory for PolygonBaseView tests."""
        self.factory = APIRequestFactory()

    def _bind_perform_request(self, view, func):
        """Bind a function as the view's perform_request for controlled upstream behavior."""
        view.perform_request = types.MethodType(func, view)

    def test_get_success_json_and_param_passing(self):
        """Exercise a successful GET flow with JSON response and verify param forwarding.

        Approach: mock perform_request to return JSON; include both query params and extra kwargs.
        Expected: 200 response, serializer-standardized payload, and perform_request receives expected
        provider URL plus merged query params (allowed params + non-placeholder kwargs).
        """
        view = PolygonEmaView()

        captured = {}

        def fake_perform_request(self, method: str, url: str, *, params=None):
            captured["method"] = method
            captured["url"] = url
            captured["params"] = list(params or [])
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {
                "results": [{"value": 123, "logo_url": "https://api.polygon.io/logo.png"}],
                "next_url": "https://api.polygon.io/v3/foo?page=2",
            }
            mock_resp.text = ""
            mock_resp.raise_for_status.return_value = None
            mock_resp.request = httpx.Request(method, url)
            return mock_resp

        bind_perform_request(view, fake_perform_request)

        django_request = self.factory.get("/x", {"series_type": "close", "window": "14"})
        request = Request(django_request)
        response = view.get(request, stockTicker="AAPL", extra="foo")

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("results", data)

        self.assertEqual(captured["method"], "GET")
        self.assertTrue(captured["url"].endswith("/v1/indicators/ema/AAPL"))

        self.assertIn(("extra", "foo"), captured["params"])
        self.assertIn(("series_type", "close"), captured["params"])

        self.assertNotIn("logo_url", data["results"][0])

        self.assertTrue(str(data.get("next_url", "")).startswith("https://financialdata.online"))

    def test_get_upstream_error_returns_502(self):
        """Ensure upstream httpx errors are translated to a 502 response.

        Approach: perform_request raises httpx.HTTPError; call get().
        Expected: Response with status 502 and no data processing.
        """

        def fake_perform_request(self, method: str, url: str, *, params=None):
            raise httpx.HTTPError("boom")

        view = PolygonEmaView()
        bind_perform_request(view, fake_perform_request)

        # Call view directly to use injected upstream_client shim
        response = view.get(Request(self.factory.get("/x")), stockTicker="AAPL")
        self.assertEqual(response.status_code, 502)

    def test_get_text_response_passthrough(self):
        """Validate non-JSON responses are passed through unchanged (content as text).

        Approach: perform_request returns text/plain.
        Expected: response.data equals the raw text 'OK' with status 200.
        """
        view = PolygonEmaView()

        def fake_perform_request(self, method: str, url: str, *, params=None):
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "text/plain"}
            mock_resp.text = "OK"
            mock_resp.raise_for_status.return_value = None
            mock_resp.request = httpx.Request(method, url)
            return mock_resp

        bind_perform_request(view, fake_perform_request)
        response = view.get(Request(self.factory.get("/x")), stockTicker="AAPL")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, "OK")

    def test_format_endpoint_to_mixed_placeholders_sources(self):
        """Ensure complex provider paths resolve placeholders from both kwargs and query params.

        Approach: use AGG_CUSTOM_RANGE requiring multiple placeholders; provide some via kwargs and
        others via query params.
        Expected: formatted path contains all provided values with no error.
        """
        view = PolygonAggView()
        request = Request(
            self.factory.get(
                "/x",
                {"multiplier": "5", "timespan": "minute", "from": "2020-01-01", "to": "2020-01-02"},
            )
        )
        path, error = view._format_endpoint_to(request, kwargs={"stocksTicker": "AAPL"})
        self.assertIsNone(error)
        self.assertIn("AAPL", path)
        self.assertIn("/range/5/minute/2020-01-01/2020-01-02", path)


class FMPBaseViewUnitTests(TestCase):
    """Integration-style tests for `FMPBaseView` and serializer standardization."""

    def setUp(self) -> None:
        """Prepare an APIRequestFactory for FMPBaseView tests."""
        self.factory = APIRequestFactory()

    def _bind_perform_request(self, view, func):
        """Bind a function as the view's perform_request for controlled upstream behavior."""
        view.perform_request = types.MethodType(func, view)

    def test_get_fmp_serializer_filters_and_standardizes(self):
        """Verify FMP serializer standardizes arrays and filters provider URLs in nested data.

        Approach: perform_request returns JSON with provider URLs; call get() with required symbol.
        Expected: 200 response, 'results' list present, and provider URL rewritten to our base.
        """
        view = FMPExecsView()

        def fake_perform_request(self, method: str, url: str, *, params=None):
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {
                "data": [
                    {
                        "name": "Alice",
                        "image_url": "https://financialmodelingprep.com/images/alice.png",
                    }
                ]
            }
            mock_resp.text = ""
            mock_resp.raise_for_status.return_value = None
            mock_resp.request = httpx.Request(method, url)
            return mock_resp

        bind_perform_request(view, fake_perform_request)
        response = view.get(Request(self.factory.get("/x")), symbol="MSFT")
        self.assertEqual(response.status_code, 200)
        payload = response.data
        self.assertIn("results", payload)
        self.assertIsInstance(payload["results"], list)

        self.assertNotIn("image_url", payload["results"][0])

    def test_fmp_standardizes_single_object_to_results_list(self):
        """Validate FMP serializer wraps single object payloads into 'results' list without count.

        Approach: perform_request returns a single dict without 'results' key.
        Expected: serializer returns {'results': [obj]}.
        """
        view = FMPAnyView()

        def fake_perform_request(self, method: str, url: str, *, params=None):
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {"company": "ACME"}
            mock_resp.text = ""
            mock_resp.raise_for_status.return_value = None
            mock_resp.request = httpx.Request(method, url)
            return mock_resp

        bind_perform_request(view, fake_perform_request)
        resp = view.get(Request(self.factory.get("/x")), symbol="ACME")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("results", resp.data)
        first = resp.data["results"][0]
        self.assertEqual(first.get("company"), "ACME")
        self.assertIn("_processed_at", first)

    def test_parse_response_invalid_json_falls_back_to_text(self):
        """Ensure _parse_response returns raw text when content-type is JSON but body is invalid JSON.

        Approach: create httpx.Response with content-type 'application/json' and invalid body; call
        _parse_response directly on a ProviderAPIView subclass (response serializer won't be used).
        Expected: returns (text, status_code).
        """

        class BareView(ProviderAPIView):
            pass

        view = BareView()
        resp = httpx.Response(200, headers={"content-type": "application/json"}, content=b"{")
        data, status_code = view._parse_response(resp)
        self.assertEqual(status_code, 200)
        self.assertEqual(data, "{")


class ProviderAPIViewAdditionalUnitTests(TestCase):
    """Additional edge cases for `ProviderAPIView` helpers and strategies."""

    def setUp(self) -> None:
        """Prepare factory for ProviderAPIView edge-case tests."""
        self.factory = APIRequestFactory()

    def test_as_path_missing_endpoint_from_raises(self):
        """as_path should raise RuntimeError when endpoint_from is not defined on the view class."""

        class NoFromView(ProviderAPIView):
            pass

        with self.assertRaises(RuntimeError):
            NoFromView.as_path()

    def test_as_path_default_name_mapping(self):
        """Default route name should derive from ClassName by removing 'View' suffix and lowercasing."""

        class PriceView(ProviderAPIView):
            endpoint_from = EndpointFrom.STOCKS_REFERENCE_NEWS

        urlpattern: URLPattern = PriceView.as_path()
        self.assertEqual(urlpattern.name, "price")

    def test_build_params_single_enum_applies_filtering(self):
        """allowed_params as a single Enum class should filter keys accordingly."""

        class SingleEnumView(ProviderAPIView):
            allowed_params = PolygonParams.Common

        view = SingleEnumView()
        request = Request(self.factory.get("/x", {"cursor": "abc", "other": "1"}))
        pairs = view.build_params(request)
        self.assertEqual(pairs, [("cursor", "abc")])

    def test_build_params_empty_iterable_filters_out_all(self):
        """Empty iterable for allowed_params results in no allowed keys (empty pairs)."""

        class EmptyAllowedView(ProviderAPIView):
            allowed_params = []

        view = EmptyAllowedView()
        request = Request(self.factory.get("/x", {"a": "1", "b": ["2", "3"]}))
        pairs = view.build_params(request)
        # With an empty iterable of enums, there are no allowed keys → empty
        self.assertEqual(pairs, [])

    def test_build_params_serializer_with_single_enum_and_non_str_values(self):
        """Serializer + single Enum allowed should filter and coerce non-string values to strings."""

        class SerView(ProviderAPIView):
            serializer_class = AnyParamsSerializer
            allowed_params = PolygonParams.IndicatorCommon

        view = SerView()
        request = Request(self.factory.get("/x", {"window": 14, "series_type": "close", "foo": True}))
        pairs = view.build_params(request)
        self.assertIn(("window", "14"), pairs)
        self.assertIn(("series_type", "close"), pairs)
        # 'foo' must be filtered out
        self.assertNotIn(("foo", "True"), pairs)

    def test_format_endpoint_to_without_placeholders_returns_path(self):
        """_format_endpoint_to should return original path and no error when there are no placeholders."""

        class NoPH(ProviderAPIView):
            endpoint_to = "/v1/no/placeholders"

        view = NoPH()
        path, error = view._format_endpoint_to(Request(self.factory.get("/x")), kwargs={})
        self.assertEqual(path, "/v1/no/placeholders")
        self.assertIsNone(error)

    def test_format_endpoint_to_uses_last_value_of_multi_query(self):
        """When query param has multiple values, ensure the resolved placeholder uses QueryDict.get semantics (last value)."""
        view = ProviderToEma()
        request = Request(self.factory.get("/x", (("stockTicker", "AAPL"), ("stockTicker", "MSFT"))))
        path, error = view._format_endpoint_to(request, kwargs={})
        self.assertIsNone(error)
        self.assertTrue(path.endswith("/MSFT"))

    def test_perform_upstream_calls_raise_for_status(self):
        """_perform_upstream must call raise_for_status on the returned response object."""

        class Bare(ProviderAPIView):
            def perform_request(self, method: str, url: str, *, params=None):
                mock_resp = MagicMock(spec=httpx.Response)
                mock_resp.raise_for_status.return_value = None
                return mock_resp

        view = Bare()
        resp = view._perform_upstream("/x", [])
        resp.raise_for_status.assert_called_once()

    def test_strategy_injection_param_builder(self):
        """ParamBuilderStrategy should be used when injected on the view, returning its result verbatim."""

        class PB:
            def build(self, view, request):
                return [("injected", "yes")]

        class V(ProviderAPIView):
            param_builder = PB()

        view = V()
        pairs = view.build_params(Request(self.factory.get("/x", {"a": "1"})))
        self.assertEqual(pairs, [("injected", "yes")])

    def test_strategy_injection_endpoint_formatter(self):
        """EndpointFormatterStrategy should override default formatting and may return errors."""

        class EF:
            def format(self, view, request, kwargs):
                return "/override", None

        class V(ProviderToEma):
            endpoint_formatter = EF()

        view = V()
        path, error = view._format_endpoint_to(Request(self.factory.get("/x")), kwargs={})
        self.assertEqual(path, "/override")
        self.assertIsNone(error)

    def test_strategy_injection_upstream_client(self):
        """UpstreamClientStrategy should be used by _perform_upstream when present (no raise_for_status required)."""

        class UC:
            def request(self, view, method, url_path, *, params=None):
                mock_resp = MagicMock(spec=httpx.Response)
                mock_resp.status_code = 200
                mock_resp.headers = {"content-type": "text/plain"}
                mock_resp.text = "OK"
                return mock_resp

        class V(PolygonEmaView):
            upstream_client = UC()

        view = V()
        resp = view.get(Request(self.factory.get("/x")), stockTicker="AAPL")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, "OK")

    def test_strategy_injection_response_parser(self):
        """ResponseParserStrategy should be used by _parse_response when present."""

        class RP:
            def parse(self, view, resp):
                return ({"ok": True}, 299)

        class V(PolygonEmaView):
            response_parser = RP()

        view = V()

        def fake(self, method: str, url: str, *, params=None):
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {"ignored": True}
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        bind_perform_request(view, fake)
        resp = view.get(Request(self.factory.get("/x")), stockTicker="AAPL")
        self.assertEqual(resp.status_code, 299)
        self.assertEqual(resp.data, {"ok": True})

    def test_parse_response_no_content_type_returns_text(self):
        """_parse_response should return raw text when content-type header is missing or empty."""

        class Bare(ProviderAPIView):
            pass

        view = Bare()
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.headers = {}
        mock_resp.text = "BODY"
        mock_resp.status_code = 201
        data, status_code = view._parse_response(mock_resp)
        self.assertEqual(status_code, 201)
        self.assertEqual(data, "BODY")

    def test_parse_response_application_json_case_insensitive_and_scalar(self):
        """_parse_response should treat content-type case-insensitively and pass through scalar JSON."""

        class Bare(ProviderAPIView):
            response_serializer_class = ProviderResponseSerializer

        view = Bare()
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.headers = {"content-type": "Application/JSON"}
        mock_resp.status_code = 200
        mock_resp.json.return_value = 123
        data, status_code = view._parse_response(mock_resp)
        self.assertEqual(status_code, 200)
        self.assertEqual(data, 123)

    def test_serialize_response_passes_current_view(self):
        """_serialize_response must instantiate serializer with current_view=self."""

        class AssertingSerializer:
            def __init__(self, current_view=None, *args, **kwargs):
                self.current_view = current_view

            def to_representation(self, data):
                return {"got_view": isinstance(self.current_view, ProviderAPIView), "data": data}

        class SView(ProviderAPIView):
            response_serializer_class = AssertingSerializer

        view = SView()
        resp = MagicMock(spec=httpx.Response)
        resp.headers = {"content-type": "application/json"}
        resp.status_code = 200
        resp.json.return_value = {"x": 1}
        data, _ = view._parse_response(resp)
        self.assertTrue(data["got_view"])  # current_view passed
        self.assertEqual(data["data"], {"x": 1})

    def test_get_current_behavior_adds_placeholder_kwarg_to_params(self):
        """Current behavior: placeholder kwargs are appended to params because placeholders are resolved before filtering unused keys."""
        view = PolygonEmaView()
        captured = {}

        def fake(self, method: str, url: str, *, params=None):
            captured["params"] = list(params or [])
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {"results": []}
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        bind_perform_request(view, fake)
        _ = view.get(Request(self.factory.get("/x", {"foo": "bar"})), stockTicker="AAPL")
        # Placeholder kwarg is currently appended because placeholder detection occurs after formatting
        self.assertIn(("stockTicker", "AAPL"), captured["params"])
        # Unrelated query params are filtered by allowed_params
        self.assertNotIn(("foo", "bar"), captured["params"])

    def test_results_key_none_skips_results_pagination_branch(self):
        """When results_key is None, get() should not enter dict-with-results pagination branch."""

        class RKNoneView(PolygonEmaView):
            results_key = None

        def fake(self, method: str, url: str, *, params=None):
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 206
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {"results": [1, 2, 3], "extra": True}
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        view = RKNoneView()
        bind_perform_request(view, fake)
        resp = view.get(Request(self.factory.get("/x")), stockTicker="AAPL")
        self.assertEqual(resp.status_code, 206)
        # payload should be returned as-is without pagination merge
        self.assertEqual(resp.data.get("extra"), True)


class PaginationBranchUnitTests(TestCase):
    """Tests for custom pagination hooks to ensure status and payload shape."""

    def setUp(self) -> None:
        """Prepare factory for pagination behavior tests with overridden hooks."""
        self.factory = APIRequestFactory()

    def test_custom_pagination_with_list_data_preserves_status(self):
        """Custom pagination hooks should be used for list data and preserve status code."""

        class PaginatedListView(PolygonEmaView):
            pagination_class = object  # sentinel to enable pagination path

            def paginate_queryset(self, data):
                return data[:1]

            def get_paginated_response(self, page):
                return Response({"results": page, "page": 1})

        view = PaginatedListView()

        def fake(self, method: str, url: str, *, params=None):
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 299
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = [1, 2, 3]
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        bind_perform_request(view, fake)
        resp = view.get(Request(self.factory.get("/x")), stockTicker="AAPL")
        self.assertEqual(resp.status_code, 299)
        self.assertEqual(resp.data.get("results"), [1])
        self.assertEqual(resp.data.get("page"), 1)

    def test_custom_pagination_with_results_dict_preserves_keys(self):
        """Custom pagination hooks should merge non-results keys into the paginated payload."""

        class PaginatedDictView(PolygonEmaView):
            pagination_class = object

            def paginate_queryset(self, data):
                return data[:1]

            def get_paginated_response(self, page):
                return Response({"results": page, "page": 2})

        view = PaginatedDictView()

        def fake(self, method: str, url: str, *, params=None):
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 207
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {"results": [10, 20], "next_url": "https://api.polygon.io/v3/foo"}
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        bind_perform_request(view, fake)
        resp = view.get(Request(self.factory.get("/x")), stockTicker="AAPL")
        self.assertEqual(resp.status_code, 207)
        self.assertEqual(resp.data.get("results"), [10])
        # next_url should be preserved (but processed by serializer to our base)
        self.assertIn("next_url", resp.data)


class PerformRequestUnitTests(TestCase):
    """Tests for upstream HTTPX client behavior on provider base views."""

    def setUp(self) -> None:
        """Prepare factory for perform_request tests and set deterministic timeouts/base URLs."""
        self.factory = APIRequestFactory()

    @patch("proxy_app.provider_api.strategies.upstream.httpx.request")
    def test_fmp_httpx_client_url_timeout_and_apikey(self, mock_request):
        """HttpxClient for FMP must join base URL, pass timeout, and append apikey when present."""

        class F(FMPBaseView):
            endpoint_to = "/v1/foo"

        view = F()
        view.timeout = 12.5

        # Prepare a fake httpx.Response-like object
        fake = MagicMock(spec=httpx.Response)
        fake.status_code = 200
        fake.headers = {"content-type": "application/json"}
        fake.json.return_value = {"results": []}
        fake.text = ""
        fake.raise_for_status.return_value = None
        mock_request.return_value = fake

        resp = view.get(Request(self.factory.get("/x")))
        self.assertEqual(resp.status_code, 200)

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].endswith("/v1/foo"))
        self.assertEqual(kwargs["timeout"], 12.5)
        self.assertIn(("apikey", settings.FMP_API_KEY), kwargs["params"])

    @patch("proxy_app.provider_api.strategies.upstream.httpx.request")
    def test_polygon_httpx_client_without_apikey(self, mock_request):
        """HttpxClient for Polygon should not append apikey when config api_key_value is empty."""
        from proxy_app.provider_api.config import ProviderConfig
        from proxy_app.provider_api.strategies.upstream import HttpxClient

        class P(PolygonBaseView):
            endpoint_to = "/v3/bar"

        view = P()
        view.timeout = 7
        # Override upstream_client with empty api key config
        view.upstream_client = HttpxClient(
            ProviderConfig(base_url="https://poly.example", api_key_param="apikey", api_key_value="", timeout=7)
        )

        fake = MagicMock(spec=httpx.Response)
        fake.status_code = 200
        fake.headers = {"content-type": "application/json"}
        fake.json.return_value = {"results": []}
        fake.text = ""
        fake.raise_for_status.return_value = None
        mock_request.return_value = fake

        resp = view.get(Request(self.factory.get("/x")))
        self.assertEqual(resp.status_code, 200)

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[1], "https://poly.example/v3/bar")
        self.assertEqual(kwargs["timeout"], 7)
        self.assertEqual(kwargs["params"], [])


class StrategyAndPaginationUnitTests(TestCase):
    """Unit tests for strategy classes, pagination behavior, and exceptions."""

    def setUp(self) -> None:
        """Prepare an `APIRequestFactory` for constructing requests in tests."""
        self.factory = APIRequestFactory()

    def test_serializer_param_builder_without_serializer(self):
        """SerializerParamBuilder should flatten values when no serializer is provided."""

        class V(ProviderAPIView):
            pass

        view = V()
        builder = SerializerParamBuilder()
        pairs = builder.build(view, Request(self.factory.get("/x", {"a": [1, 2], "b": 3})))
        self.assertCountEqual(pairs, [("a", "1"), ("a", "2"), ("b", "3")])

    def test_curly_placeholder_formatter_missing(self):
        """CurlyPlaceholderFormatter should return 400 error response when missing a value."""

        class V(ProviderAPIView):
            endpoint_to = "/v1/{id}/x"

        fmt = CurlyPlaceholderFormatter()
        path, error = fmt.format(V(), Request(self.factory.get("/x")), kwargs={})
        self.assertEqual(path, "")
        self.assertIsNotNone(error)

    def test_json_or_text_parser_uses_serializer(self):
        """JsonOrTextParser should wrap JSON via the view's serializer class."""

        class S:
            def __init__(self, current_view=None, *args, **kwargs):
                self.view = current_view

            def to_representation(self, data):
                return {"wrapped": data}

        class V(ProviderAPIView):
            response_serializer_class = S

        parser = JsonOrTextParser()
        resp = MagicMock(spec=httpx.Response)
        resp.headers = {"content-type": "application/json"}
        resp.status_code = 200
        resp.json.return_value = {"x": 1}
        data, status_code = parser.parse(V(), resp)
        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"wrapped": {"x": 1}})

    def test_results_key_pagination_with_dict_and_none_results_key(self):
        """ResultsKeyPagination should skip dict pagination when `results_key` is None."""

        class V(ProviderAPIView):
            results_key = None
            pagination_class = ResultsKeyPagination

        view = V()
        request = Request(self.factory.get("/x"))
        view.request = request  # type: ignore[attr-defined]
        data = {"results": [1, 2], "meta": True}
        page = view.paginate_queryset(data)
        self.assertIsNone(page)  # not paginated when results_key is None

    def test_provider_config_direct_construction(self):
        """ProviderConfig should be directly constructible from settings values."""
        f = ProviderConfig(base_url=settings.FMP_BASE_URL, api_key_param="apikey", api_key_value=settings.FMP_API_KEY, timeout=1.5)
        p = ProviderConfig(base_url=settings.POLYGON_BASE_URL, api_key_param="apikey", api_key_value=settings.POLYGON_API_KEY, timeout=2.5)
        self.assertIsInstance(f, ProviderConfig)
        self.assertIsInstance(p, ProviderConfig)

    def test_provider_config_is_frozen(self):
        """ProviderConfig must be immutable (frozen dataclass protects attributes)."""
        cfg = ProviderConfig(base_url="https://x", api_key_param="k", api_key_value="v", timeout=1.0)
        with self.assertRaises(Exception):
            # Dataclasses use FrozenInstanceError, but guard with generic Exception to avoid import coupling
            cfg.base_url = "https://y"  # type: ignore[misc]

    @patch("proxy_app.provider_api.strategies.upstream.httpx.request")
    def test_httpx_client_request_builds_url_and_params(self, mock_request):
        """HttpxClient should build full URL, append API key, and pass timeout/params."""
        cfg = ProviderConfig(base_url="https://api.example", api_key_param="key", api_key_value="VAL", timeout=3.0)
        client = HttpxClient(cfg)

        fake = MagicMock(spec=httpx.Response)
        fake.status_code = 200
        fake.headers = {"content-type": "application/json"}
        fake.json.return_value = {}
        fake.raise_for_status.return_value = None
        mock_request.return_value = fake

        _ = client.request(view=None, method="GET", url_path="/v1/test", params=[("a", "1")])

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "https://api.example/v1/test")
        self.assertIn(("a", "1"), kwargs["params"])
        self.assertIn(("key", "VAL"), kwargs["params"])
        self.assertEqual(kwargs["timeout"], 3.0)

    def test_results_key_pagination_with_list(self):
        """ResultsKeyPagination should paginate simple list payloads and return `results`."""

        class V(ProviderAPIView):
            pagination_class = ResultsKeyPagination

        view = V()
        request = Request(self.factory.get("/x"))
        view.request = request  # type: ignore[attr-defined]
        data = [1, 2, 3]
        page = view.paginate_queryset(data)
        self.assertIsNotNone(page)
        resp = view.get_paginated_response(page)
        self.assertIn("results", resp.data)

    def test_results_key_pagination_with_dict_and_preserved(self):
        """ResultsKeyPagination should preserve non-results keys when paginating dict payloads."""

        class V(ProviderAPIView):
            pagination_class = ResultsKeyPagination
            results_key = "results"

        view = V()
        request = Request(self.factory.get("/x"))
        view.request = request  # type: ignore[attr-defined]
        data = {"results": [10, 20], "meta": True}
        page = view.paginate_queryset(data)
        self.assertIsNotNone(page)
        resp = view.get_paginated_response(page)
        # Preserved keys should exist
        self.assertTrue(resp.data.get("meta"))

    def test_upstream_api_exception_default(self):
        """UpstreamAPIException should default to 502 with a `detail` field in payload."""
        exc = UpstreamAPIException()
        self.assertEqual(exc.status_code, 502)
        # default_detail may be used by DRF when detail omitted
        self.assertIn("detail", exc.default_detail)

    def test_upstream_api_exception_via_view(self):
        """Views raising UpstreamAPIException should be rendered as 502 by DRF handler."""

        class V(ProviderAPIView):
            endpoint_to = "/x"

            def get(self, request, *args, **kwargs):
                raise UpstreamAPIException()

        django_request = self.factory.get("/x")
        response = V.as_view()(django_request)
        self.assertEqual(response.status_code, 502)
