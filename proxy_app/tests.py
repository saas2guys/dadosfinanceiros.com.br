from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.test.client import RequestFactory

from proxy_app.views import PolygonProxyView


class PolygonProxyViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = PolygonProxyView()

    def test_replace_polygon_urls(self):
        """Test that Polygon URLs are replaced with proxy domain."""
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

    def test_replace_multiple_pagination_fields(self):
        """Test URL replacement for multiple pagination fields."""
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

    def test_no_polygon_urls(self):
        """Test that data without Polygon URLs remains unchanged."""
        request = self.factory.get("/test/")

        test_data = {
            "status": "OK",
            "count": 100,
            "results": [{"ticker": "AAPL", "price": 150.25}],
        }

        original_data = test_data.copy()
        result = self.view._replace_polygon_urls(test_data, request)

        self.assertEqual(result, original_data)

    def test_non_dict_data(self):
        """Test that non-dictionary data is returned unchanged."""
        request = self.factory.get("/test/")

        test_data = ["some", "list", "data"]
        result = self.view._replace_polygon_urls(test_data, request)

        self.assertEqual(result, test_data)

    def test_exact_user_example(self):
        """Test with the exact response format provided by the user."""
        request = self.factory.get("/test/")

        test_data = {
            "count": 1,
            "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy",
            "request_id": "e70013d92930de90e089dc8fa098888e",
            "results": [
                {
                    "active": True,
                    "cik": "0001090872",
                    "composite_figi": "BBG000BWQYZ5",
                    "currency_name": "usd",
                    "last_updated_utc": "2021-04-25T00:00:00Z",
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
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["request_id"], "e70013d92930de90e089dc8fa098888e")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["ticker"], "A")

    def test_process_response_removes_status_key(self):
        request = self.factory.get("/test/")
        
        mock_response = MagicMock()
        mock_response.content = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "count": 1,
            "results": [{"ticker": "AAPL", "price": 150.25}],
            "request_id": "test123"
        }

        result = self.view._process_response(mock_response, request)
        
        self.assertEqual(result.status_code, 200)
        self.assertNotIn("status", result.data)
        self.assertIn("count", result.data)
        self.assertIn("results", result.data)
        self.assertIn("request_id", result.data)

    def test_process_response_removes_status_key_with_pagination(self):
        request = self.factory.get("/test/")
        
        mock_response = MagicMock()
        mock_response.content = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "count": 1,
            "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=test123&apikey=secret",
            "results": [{"ticker": "AAPL", "price": 150.25}]
        }

        result = self.view._process_response(mock_response, request)
        
        self.assertEqual(result.status_code, 200)
        self.assertNotIn("status", result.data)
        self.assertIn("count", result.data)
        self.assertIn("results", result.data)
        self.assertIn("next_url", result.data)
        expected_next_url = "https://api.dadosfinanceiros.com.br/v1/reference/tickers?cursor=test123"
        self.assertEqual(result.data["next_url"], expected_next_url)

    def test_process_response_no_status_key(self):
        request = self.factory.get("/test/")
        
        mock_response = MagicMock()
        mock_response.content = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "count": 1,
            "results": [{"ticker": "AAPL", "price": 150.25}]
        }

        result = self.view._process_response(mock_response, request)
        
        self.assertEqual(result.status_code, 200)
        self.assertNotIn("status", result.data)
        self.assertIn("count", result.data)
        self.assertIn("results", result.data)
