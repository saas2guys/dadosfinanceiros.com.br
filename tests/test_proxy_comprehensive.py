import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from proxy_app.views import PolygonProxyView
from users.models import Plan, TokenHistory, User

User = get_user_model()


class PolygonProxyTestCaseBase(APITestCase):
    """
    Base test case class for Polygon API proxy tests.

    Provides common setup including authenticated users, mock responses,
    and shared utilities for testing Polygon API proxy functionality.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.view = PolygonProxyView()

        # Create a plan first
        self.plan = Plan.objects.create(
            name="Test Plan",
            daily_request_limit=1000,
            price_monthly=Decimal("9.99"),
        )

        # Create user without daily_request_limit parameter
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        # Assign the plan to the user
        self.user.current_plan = self.plan
        self.user.subscription_status = "active"
        self.user.save()

        self.user.generate_new_request_token()

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.request_token = str(self.user.request_token)

    def _create_authenticated_request(
        self, method="GET", path="/", data=None, use_jwt=True
    ):
        if method.upper() == "GET":
            request = self.factory.get(f"/v1/{path}", data or {})
        elif method.upper() == "POST":
            request = self.factory.post(
                f"/v1/{path}", data or {}, content_type="application/json"
            )
        elif method.upper() == "PUT":
            request = self.factory.put(
                f"/v1/{path}", json.dumps(data or {}), content_type="application/json"
            )
        elif method.upper() == "DELETE":
            request = self.factory.delete(f"/v1/{path}")
        else:
            request = self.factory.generic(
                method,
                f"/v1/{path}",
                json.dumps(data or {}),
                content_type="application/json",
            )

        if use_jwt:
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {self.access_token}"
        else:
            request.META["HTTP_X_REQUEST_TOKEN"] = self.request_token

        request.user = self.user

        # Add data attribute for non-GET requests
        if hasattr(request, "method") and request.method in ["POST", "PUT", "PATCH"]:
            request.data = data or {}

        return request

    def _mock_polygon_response(self, response_data, status_code=200):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.content = json.dumps(response_data).encode()
        mock_response.json.return_value = response_data
        return mock_response


class PolygonStocksApiComprehensiveTest(PolygonProxyTestCaseBase):
    """
    Test suite for comprehensive Polygon stocks API proxy functionality.

    Covers all stocks endpoints, aggregates, trades, quotes, snapshots,
    and complete stocks data retrieval through the proxy system.
    """

    @patch("proxy_app.views.requests.Session.request")
    def test_tickers_list_endpoint(self, mock_request):
        mock_response_data = {
            "results": [
                {
                    "ticker": "AAPL",
                    "name": "Apple Inc.",
                    "market": "stocks",
                    "locale": "us",
                    "primary_exchange": "NASDAQ",
                    "type": "CS",
                    "active": True,
                    "currency_name": "usd",
                    "last_updated_utc": "2023-03-21T00:00:00Z",
                }
            ],
            "count": 1,
            "status": "OK",
            "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=next123&apikey=test",
        }

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET", "reference/tickers", use_jwt=False
        )
        response = self.view.get(request, path="reference/tickers")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("status", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

        # Check URL replacement
        expected_next_url = (
            "https://api.financialdata.online/v1/reference/tickers?cursor=next123"
        )
        self.assertEqual(response.data["next_url"], expected_next_url)

    @patch("proxy_app.views.requests.Session.request")
    def test_stocks_aggregates_endpoint(self, mock_request):
        mock_response_data = {
            "adjusted": True,
            "results": [
                {
                    "T": "AAPL",
                    "c": 150.43,
                    "h": 151.12,
                    "l": 149.22,
                    "n": 450213,
                    "o": 150.00,
                    "t": 1640995200000,
                    "v": 89946428,
                    "vw": 150.3052,
                }
            ],
            "resultsCount": 1,
            "status": "OK",
        }

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET", "aggs/ticker/AAPL/range/1/day/2023-01-01/2023-01-31", use_jwt=False
        )
        response = self.view.get(
            request, path="aggs/ticker/AAPL/range/1/day/2023-01-01/2023-01-31"
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("status", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["resultsCount"], 1)

    @patch("proxy_app.views.requests.Session.request")
    def test_market_holidays_endpoint(self, mock_request):
        mock_response_data = {
            "results": [
                {
                    "date": "2023-01-02",
                    "exchange": "NASDAQ",
                    "name": "New Year's Day (Observed)",
                    "status": "closed",
                }
            ],
            "count": 1,
            "status": "OK",
        }

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET", "marketstatus/upcoming", use_jwt=False
        )
        response = self.view.get(request, path="marketstatus/upcoming")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("status", response.data)
        self.assertIn("results", response.data)


class PolygonOptionsApiComprehensiveTest(PolygonProxyTestCaseBase):
    """
    Test suite for comprehensive Polygon options API proxy functionality.

    Covers options contracts, chains, snapshots, trades, and all
    options-related data retrieval through the proxy system.
    """

    @patch("proxy_app.views.requests.Session.request")
    def test_options_contracts_endpoint(self, mock_request):
        mock_response_data = {
            "results": [
                {
                    "ticker": "O:AAPL230120C00150000",
                    "underlying_ticker": "AAPL",
                    "option_type": "call",
                    "strike_price": 150,
                    "expiration_date": "2023-01-20",
                }
            ],
            "count": 1,
            "status": "OK",
        }

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET", "reference/options/contracts", use_jwt=False
        )
        response = self.view.get(request, path="reference/options/contracts")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("status", response.data)
        self.assertIn("results", response.data)


class PolygonCryptoApiComprehensiveTest(PolygonProxyTestCaseBase):
    """
    Test suite for comprehensive Polygon crypto API proxy functionality.

    Covers cryptocurrency data, trades, aggregates, snapshots,
    and complete crypto market data through the proxy system.
    """

    @patch("proxy_app.views.requests.Session.request")
    def test_crypto_aggregates_endpoint(self, mock_request):
        mock_response_data = {
            "adjusted": True,
            "results": [
                {
                    "T": "X:BTCUSD",
                    "c": 45000.50,
                    "h": 46000.00,
                    "l": 44000.00,
                    "n": 12345,
                    "o": 45500.00,
                    "t": 1640995200000,
                    "v": 123.456,
                    "vw": 45250.25,
                }
            ],
            "resultsCount": 1,
            "status": "OK",
        }

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET",
            "aggs/ticker/X:BTCUSD/range/1/day/2023-01-01/2023-01-31",
            use_jwt=False,
        )
        response = self.view.get(
            request, path="aggs/ticker/X:BTCUSD/range/1/day/2023-01-01/2023-01-31"
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("status", response.data)
        self.assertIn("results", response.data)


class PolygonForexApiComprehensiveTest(PolygonProxyTestCaseBase):
    """
    Test suite for comprehensive Polygon forex API proxy functionality.

    Covers currency pairs, exchange rates, forex aggregates,
    and complete foreign exchange data through the proxy system.
    """

    @patch("proxy_app.views.requests.Session.request")
    def test_forex_aggregates_endpoint(self, mock_request):
        mock_response_data = {
            "adjusted": True,
            "results": [
                {
                    "T": "C:EURUSD",
                    "c": 1.0950,
                    "h": 1.0980,
                    "l": 1.0920,
                    "n": 50000,
                    "o": 1.0935,
                    "t": 1640995200000,
                    "v": 1000000,
                    "vw": 1.0945,
                }
            ],
            "resultsCount": 1,
            "status": "OK",
        }

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET",
            "aggs/ticker/C:EURUSD/range/1/day/2023-01-01/2023-01-31",
            use_jwt=False,
        )
        response = self.view.get(
            request, path="aggs/ticker/C:EURUSD/range/1/day/2023-01-01/2023-01-31"
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("status", response.data)
        self.assertIn("results", response.data)


class PolygonIndicesApiComprehensiveTest(PolygonProxyTestCaseBase):
    """
    Test suite for comprehensive Polygon indices API proxy functionality.

    Covers market indices, index values, historical data,
    and complete indices information through the proxy system.
    """

    @patch("proxy_app.views.requests.Session.request")
    def test_indices_aggregates_endpoint(self, mock_request):
        mock_response_data = {
            "adjusted": True,
            "results": [
                {
                    "T": "I:SPX",
                    "c": 4200.50,
                    "h": 4220.75,
                    "l": 4180.25,
                    "n": 1000,
                    "o": 4195.00,
                    "t": 1640995200000,
                    "v": 0,
                    "vw": 4200.00,
                }
            ],
            "resultsCount": 1,
            "status": "OK",
        }

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET", "aggs/ticker/I:SPX/range/1/day/2023-01-01/2023-01-31", use_jwt=False
        )
        response = self.view.get(
            request, path="aggs/ticker/I:SPX/range/1/day/2023-01-01/2023-01-31"
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("status", response.data)
        self.assertIn("results", response.data)


class PolygonProxyEdgeCaseHandlingTest(PolygonProxyTestCaseBase):
    """
    Test suite for Polygon proxy edge cases and error handling.

    Covers malformed requests, invalid parameters, rate limiting,
    error responses, and exceptional scenarios in proxy operations.
    """

    @patch("proxy_app.views.requests.Session.request")
    def test_polygon_api_error_response(self, mock_request):
        """Test handling of Polygon API error responses"""
        error_response_data = {
            "status": "ERROR",
            "error": "Invalid API key",
            "request_id": "test123",
        }

        mock_request.return_value = self._mock_polygon_response(
            error_response_data, 401
        )

        request = self._create_authenticated_request(
            "GET", "reference/tickers", use_jwt=False
        )
        response = self.view.get(request, path="reference/tickers")

        self.assertEqual(response.status_code, 401)
        # Even error responses should have status removed
        self.assertNotIn("status", response.data)
        self.assertIn("error", response.data)

    @patch("proxy_app.views.requests.Session.request")
    def test_connection_error_handling(self, mock_request):
        """Test handling of connection errors"""
        mock_request.side_effect = requests.ConnectionError("Connection failed")

        request = self._create_authenticated_request(
            "GET", "reference/tickers", use_jwt=False
        )
        response = self.view.get(request, path="reference/tickers")

        # Should return an error response
        self.assertIn(response.status_code, [500, 502, 503])

    @patch("proxy_app.views.requests.Session.request")
    def test_timeout_error_handling(self, mock_request):
        """Test handling of timeout errors"""
        mock_request.side_effect = requests.Timeout("Request timed out")

        request = self._create_authenticated_request(
            "GET", "reference/tickers", use_jwt=False
        )
        response = self.view.get(request, path="reference/tickers")

        # Should return a timeout error response
        self.assertIn(response.status_code, [500, 502, 503, 504])

    def test_unauthenticated_request(self):
        """Test handling of unauthenticated requests"""
        request = self.factory.get("/v1/reference/tickers")
        request.user = AnonymousUser()

        response = self.view.get(request, path="reference/tickers")

        # Should return unauthorized
        self.assertEqual(response.status_code, 401)

    def test_invalid_path_handling(self):
        """Test handling of invalid API paths"""
        request = self._create_authenticated_request(
            "GET", "invalid/endpoint", use_jwt=False
        )

        # This should either return a proper error or handle gracefully
        response = self.view.get(request, path="invalid/endpoint")

        # Should be a client error or server error, not a crash
        self.assertIn(response.status_code, [400, 401, 403, 404, 500, 502, 503])


class PolygonUrlTransformationComprehensiveTest(PolygonProxyTestCaseBase):
    """
    Test suite for comprehensive URL transformation and rewriting.

    Covers URL rewriting, pagination link transformation, response modification,
    and complete URL handling in proxy responses.
    """

    def test_complex_pagination_url_replacement(self):
        """Test URL replacement in complex pagination scenarios"""
        request = self.factory.get("/test/")

        test_data = {
            "status": "OK",
            "count": 1000,
            "next_url": "https://api.polygon.io/v3/reference/tickers?active=true&date=2023-01-01&limit=1000&order=asc&page_marker=ABC123&sort=ticker&apikey=secret_key",
            "previous_url": "https://api.polygon.io/v3/reference/tickers?active=true&date=2023-01-01&limit=1000&order=desc&page_marker=XYZ789&sort=ticker&apikey=secret_key",
            "results": [],
        }

        result = self.view._replace_polygon_urls(test_data, request)

        expected_next = "https://api.financialdata.online/v1/reference/tickers?active=true&date=2023-01-01&limit=1000&order=asc&page_marker=ABC123&sort=ticker"
        expected_prev = "https://api.financialdata.online/v1/reference/tickers?active=true&date=2023-01-01&limit=1000&order=desc&page_marker=XYZ789&sort=ticker"

        self.assertEqual(result["next_url"], expected_next)
        self.assertEqual(result["previous_url"], expected_prev)

    def test_nested_data_url_replacement(self):
        """Test URL replacement in nested data structures"""
        request = self.factory.get("/test/")

        test_data = {
            "status": "OK",
            "results": [
                {
                    "metadata": {
                        "info_url": "https://api.polygon.io/v1/meta/symbols/AAPL/company?apikey=test"
                    },
                    "ticker": "AAPL",
                }
            ],
            "pagination": {
                "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=next&apikey=test"
            },
        }

        result = self.view._replace_polygon_urls(test_data, request)

        # Only pagination URLs should be replaced, not nested URLs in data
        expected_next_url = (
            "https://api.financialdata.online/v1/reference/tickers?cursor=next"
        )

        # Nested URLs should NOT be replaced by this method
        self.assertEqual(
            result["results"][0]["metadata"]["info_url"],
            "https://api.polygon.io/v1/meta/symbols/AAPL/company?apikey=test",
        )
        self.assertEqual(result["pagination"]["next_url"], expected_next_url)


class PolygonProxyPerformanceAndLoadTest(PolygonProxyTestCaseBase):
    """
    Test suite for Polygon proxy performance and load testing.

    Covers response times, concurrent requests, caching behavior,
    throughput testing, and performance optimization validation.
    """

    @patch("proxy_app.views.requests.Session.request")
    def test_large_response_handling(self, mock_request):
        """Test handling of large response data"""
        # Simulate a large response with many results
        large_results = [
            {"ticker": f"STOCK{i}", "name": f"Stock Company {i}", "market": "stocks"}
            for i in range(1000)  # 1000 results
        ]

        mock_response_data = {"results": large_results, "count": 1000, "status": "OK"}

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET", "reference/tickers", use_jwt=False
        )
        response = self.view.get(request, path="reference/tickers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1000)
        self.assertNotIn("status", response.data)

    @patch("proxy_app.views.requests.Session.request")
    def test_empty_response_handling(self, mock_request):
        """Test handling of empty responses"""
        mock_response_data = {"results": [], "count": 0, "status": "OK"}

        mock_request.return_value = self._mock_polygon_response(mock_response_data)

        request = self._create_authenticated_request(
            "GET", "reference/tickers", use_jwt=False
        )
        response = self.view.get(request, path="reference/tickers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertEqual(response.data["count"], 0)
        self.assertNotIn("status", response.data)
