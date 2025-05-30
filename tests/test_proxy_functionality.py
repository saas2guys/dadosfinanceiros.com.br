from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.test.client import RequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

from proxy_app.views import PolygonProxyView
from users.models import Plan, User


class PolygonApiResponseTransformationTest(TestCase):
    """
    Test suite for the Polygon API response transformation functionality.

    Covers URL replacement, pagination field handling, response filtering,
    and all data transformation logic for proxying Polygon.io API responses.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.view = PolygonProxyView()

    def test_replaces_polygon_urls_with_proxy_domain_in_responses(self):
        request = self.factory.get("/test/")

        test_data = {
            "count": 1,
            "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy&apikey=test123",
            "request_id": "e70013d92930de90e089dc8fa098888e",
            "results": [{"ticker": "A", "name": "Agilent Technologies Inc."}],
            "status": "OK",
        }

        result = self.view._replace_polygon_urls(test_data, request)

        expected_url = "https://api.dadosfinanceiros.com.br/v1/reference/tickers?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy"
        self.assertEqual(result["next_url"], expected_url)

    def test_replaces_multiple_pagination_urls_in_single_response(self):
        request = self.factory.get("/test/")

        test_data = {
            "status": "OK",
            "next_url": "https://api.polygon.io/v2/stocks/tickers?cursor=next123&apikey=secret",
            "previous_url": "https://api.polygon.io/v2/stocks/tickers?cursor=prev456&apikey=secret",
            "results": [],
        }

        result = self.view._replace_polygon_urls(test_data, request)

        expected_next = (
            "https://api.dadosfinanceiros.com.br/v1/stocks/tickers?cursor=next123"
        )
        expected_prev = (
            "https://api.dadosfinanceiros.com.br/v1/stocks/tickers?cursor=prev456"
        )

        self.assertEqual(result["next_url"], expected_next)
        self.assertEqual(result["previous_url"], expected_prev)

    def test_preserves_non_url_fields_during_transformation(self):
        request = self.factory.get("/test/")

        test_data = {
            "count": 1,
            "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy&apikey=test123",
            "request_id": "e70013d92930de90e089dc8fa098888e",
            "results": [
                {
                    "active": True,
                    "cik": "0001045810",
                    "composite_figi": "BBG000C2V3D6",
                    "currency_name": "usd",
                    "delisted_utc": None,
                    "last_updated_utc": "2023-01-09T00:00:00Z",
                    "locale": "us",
                    "market": "stocks",
                    "name": "Agilent Technologies Inc.",
                    "primary_exchange": "XNYS",
                    "share_class_figi": "BBG001SCTQY4",
                    "ticker": "A",
                    "type": "CS",
                }
            ],
            "status": "OK",
        }

        result = self.view._replace_polygon_urls(test_data, request)

        expected_url = "https://api.dadosfinanceiros.com.br/v1/reference/tickers?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy"
        self.assertEqual(result["next_url"], expected_url)

        self.assertEqual(result["count"], 1)
        # Note: _replace_polygon_urls doesn't remove status/request_id, _process_response does
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["request_id"], "e70013d92930de90e089dc8fa098888e")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["ticker"], "A")

    def test_removes_polygon_internal_status_field_from_response(self):
        request = self.factory.get("/test/")

        mock_response = MagicMock()
        mock_response.content = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "count": 1,
            "results": [{"ticker": "AAPL", "price": 150.25}],
            "request_id": "test123",
        }

        result = self.view._process_response(mock_response, request)

        self.assertEqual(result.status_code, 200)
        # Both status and request_id should be removed
        self.assertNotIn("status", result.data)
        self.assertNotIn("request_id", result.data)
        self.assertIn("count", result.data)
        self.assertIn("results", result.data)

    def test_removes_internal_fields_while_preserving_pagination_urls(self):
        request = self.factory.get("/test/")

        mock_response = MagicMock()
        mock_response.content = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "count": 1,
            "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=test123&apikey=secret",
            "results": [{"ticker": "AAPL", "price": 150.25}],
        }

        result = self.view._process_response(mock_response, request)

        self.assertEqual(result.status_code, 200)
        self.assertNotIn("status", result.data)
        self.assertIn("count", result.data)
        self.assertIn("results", result.data)
        self.assertIn("next_url", result.data)
        expected_next_url = (
            "https://api.dadosfinanceiros.com.br/v1/reference/tickers?cursor=test123"
        )
        self.assertEqual(result.data["next_url"], expected_next_url)

    def test_handles_responses_without_internal_status_fields(self):
        request = self.factory.get("/test/")

        mock_response = MagicMock()
        mock_response.content = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "count": 1,
            "results": [{"ticker": "AAPL", "price": 150.25}],
        }

        result = self.view._process_response(mock_response, request)

        self.assertEqual(result.status_code, 200)
        self.assertNotIn("status", result.data)
        self.assertIn("count", result.data)
        self.assertIn("results", result.data)


class ProxyViewTestCaseBase(TestCase):
    """
    Base test case class for proxy view tests.

    Provides common setup including user creation, plan assignment,
    authentication tokens, and factory methods for testing proxy functionality.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.view = PolygonProxyView()

        # Create a plan first
        self.plan = Plan.objects.create(
            name="Test Plan",
            slug="test-plan",
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

        self.request_token = str(self.user.request_token)

        # For JWT authentication
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
