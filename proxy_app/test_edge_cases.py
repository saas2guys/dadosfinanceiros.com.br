import json
import time
from unittest.mock import MagicMock, patch
from django.test import TestCase, RequestFactory, override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import requests

from proxy_app.tests import BaseProxyTestCase
from users.models import User


class SecurityTests(BaseProxyTestCase):

    def test_api_key_not_exposed_in_logs(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            args, kwargs = mock_request.call_args
            self.assertIn('apiKey', kwargs['params'])
            
            with patch('proxy_app.views.logger') as mock_logger:
                self.view.get(request, 'stocks/tickers/')
                
                for call in mock_logger.info.call_args_list:
                    log_message = str(call)
                    self.assertNotIn('apiKey', log_message)
                    self.assertNotIn('apikey', log_message.lower())

    def test_request_token_not_exposed_in_response(self):
        request = self._create_authenticated_request('GET', 'stocks/tickers/', use_jwt=False)
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            response = self.view.get(request, 'stocks/tickers/')
            
            response_content = json.dumps(response.data)
            self.assertNotIn(self.request_token, response_content)

    def test_sensitive_headers_excluded(self):
        request = self._create_authenticated_request('GET', 'stocks/tickers/')
        request.META.update({
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}',
            'HTTP_X_REQUEST_TOKEN': self.request_token,
            'HTTP_HOST': 'localhost:8000',
            'HTTP_CONNECTION': 'keep-alive',
            'CONTENT_LENGTH': '100'
        })
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            self.view.get(request, 'stocks/tickers/')
            
            args, kwargs = mock_request.call_args
            headers = kwargs.get('headers', {})
            
            excluded_headers = {
                'host', 'connection', 'content-length', 'authorization', 'x-request-token'
            }
            
            for header in excluded_headers:
                self.assertNotIn(header, headers)
                self.assertNotIn(header.upper(), headers)

    def test_sql_injection_attempt_in_parameters(self):
        malicious_params = {
            'ticker': "'; DROP TABLE users; --",
            'limit': "1000; DELETE FROM users;",
            'order': "asc' OR '1'='1"
        }
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/', malicious_params)
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 200)
            args, kwargs = mock_request.call_args
            
            forwarded_params = kwargs['params']
            for key, value in malicious_params.items():
                self.assertEqual(forwarded_params[key], value)

    def test_xss_attempt_in_parameters(self):
        xss_params = {
            'search': '<script>alert("xss")</script>',
            'ticker': '<img src=x onerror=alert(1)>',
            'name': 'test<svg onload=alert(1)>'
        }
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/', xss_params)
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 200)
            
            response_content = json.dumps(response.data)
            for value in xss_params.values():
                self.assertNotIn(value, response_content)

    def test_path_traversal_attempt(self):
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
            'stocks/../../../admin/users'
        ]
        
        for malicious_path in malicious_paths:
            with patch('proxy_app.views.requests.Session.request') as mock_request:
                mock_request.return_value = self._mock_polygon_response({"results": []})
                
                request = self._create_authenticated_request('GET', malicious_path)
                response = self.view.get(request, malicious_path)
                
                args, kwargs = mock_request.call_args
                self.assertIn('polygon.io', kwargs['url'])

    def test_large_payload_handling(self):
        large_data = {'data': 'x' * 10000}
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"success": True})
            
            request = self._create_authenticated_request('POST', 'stocks/test/', large_data)
            response = self.view.post(request, 'stocks/test/')
            
            self.assertEqual(response.status_code, 200)


class EdgeCaseTests(BaseProxyTestCase):

    def test_empty_response_handling(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b''
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, {})

    def test_null_response_handling(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'null'
            mock_response.json.return_value = None
            mock_request.return_value = mock_response
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.data)

    def test_unicode_ticker_handling(self):
        unicode_params = {
            'ticker': 'AAPL测试',
            'search': 'Apple公司',
            'name': 'Тест股票'
        }
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/', unicode_params)
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 200)
            
            args, kwargs = mock_request.call_args
            for key, value in unicode_params.items():
                self.assertEqual(kwargs['params'][key], value)

    def test_special_characters_in_path(self):
        special_paths = [
            'stocks/A@B/details',
            'stocks/C%26D/details',
            'stocks/E+F/details',
            'forex/EUR:USD/rates'
        ]
        
        for path in special_paths:
            with patch('proxy_app.views.requests.Session.request') as mock_request:
                mock_request.return_value = self._mock_polygon_response({"results": []})
                
                request = self._create_authenticated_request('GET', path)
                response = self.view.get(request, path)
                
                self.assertEqual(response.status_code, 200)

    def test_extremely_long_ticker_symbol(self):
        long_ticker = 'A' * 1000
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            request = self._create_authenticated_request('GET', f'stocks/{long_ticker}/details/')
            response = self.view.get(request, f'stocks/{long_ticker}/details/')
            
            self.assertEqual(response.status_code, 200)

    def test_nested_json_response_with_urls(self):
        nested_response = {
            "data": {
                "nested": {
                    "deep": {
                        "next_url": "https://api.polygon.io/v3/test?apikey=secret"
                    }
                },
                "array": [
                    {"next_url": "https://api.polygon.io/v2/test?apikey=secret"}
                ]
            },
            "next_url": "https://api.polygon.io/v1/test?apikey=secret"
        }
        
        request = self._create_authenticated_request('GET', 'stocks/tickers/')
        result = self.view._replace_polygon_urls(nested_response, request)
        
        self.assertIn('api.dadosfinanceiros.com.br', result["next_url"])
        self.assertNotIn('apikey', result["next_url"])

    def test_malformed_pagination_url(self):
        malformed_response = {
            "next_url": "not-a-valid-url",
            "previous_url": "https://api.polygon.io/invalid-format",
            "results": []
        }
        
        request = self._create_authenticated_request('GET', 'stocks/tickers/')
        result = self.view._replace_polygon_urls(malformed_response, request)
        
        self.assertEqual(result["next_url"], "not-a-valid-url")
        self.assertEqual(result["previous_url"], "https://api.polygon.io/invalid-format")

    def test_circular_json_data_handling(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"results": []}'
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_request.return_value = mock_response
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn('Invalid JSON response', response.data['error'])

    def test_mixed_case_pagination_fields(self):
        mixed_case_response = {
            "Next_Url": "https://api.polygon.io/v3/test?apikey=secret",
            "PREVIOUS_URL": "https://api.polygon.io/v3/test?apikey=secret",
            "next_url": "https://api.polygon.io/v3/test?apikey=secret"
        }
        
        request = self._create_authenticated_request('GET', 'stocks/tickers/')
        result = self.view._replace_polygon_urls(mixed_case_response, request)
        
        self.assertEqual(result["Next_Url"], mixed_case_response["Next_Url"])
        self.assertEqual(result["PREVIOUS_URL"], mixed_case_response["PREVIOUS_URL"])
        self.assertIn('api.dadosfinanceiros.com.br', result["next_url"])


class PerformanceTests(BaseProxyTestCase):

    def test_response_time_under_load(self):
        start_time = time.time()
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            for i in range(10):
                request = self._create_authenticated_request('GET', 'stocks/tickers/')
                response = self.view.get(request, 'stocks/tickers/')
                self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.assertLess(total_time, 5.0)

    def test_large_response_processing(self):
        large_results = [
            {
                "ticker": f"TEST{i}",
                "name": f"Test Company {i}",
                "market": "stocks",
                "active": True
            }
            for i in range(1000)
        ]
        
        large_response = {
            "results": large_results,
            "count": 1000,
            "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=test&apikey=secret"
        }
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response(large_response)
            
            start_time = time.time()
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['results']), 1000)
            self.assertLess(processing_time, 2.0)

    def test_concurrent_user_simulation(self):
        users = []
        for i in range(5):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                password='testpass123'
            )
            users.append(user)
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            requests_made = []
            
            for user in users:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                request = self._create_authenticated_request('GET', 'stocks/tickers/')
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
                request.user = user
                
                response = self.view.get(request, 'stocks/tickers/')
                requests_made.append(response.status_code)
            
            self.assertEqual(len(requests_made), 5)
            self.assertTrue(all(code == 200 for code in requests_made))


class IntegrationTests(BaseProxyTestCase):

    def test_end_to_end_stocks_workflow(self):
        endpoints = [
            ('stocks/tickers/', {'market': 'stocks', 'active': 'true'}),
            ('stocks/AAPL/details/', {}),
            ('stocks/AAPL/aggregates/', {'multiplier': '1', 'timespan': 'day', 'from_date': '2023-01-01', 'to_date': '2023-01-10'}),
            ('stocks/AAPL/previous/', {'adjusted': 'true'}),
            ('stocks/AAPL/trades/', {'timestamp': '2023-01-09', 'limit': '10'}),
            ('stocks/AAPL/quotes/', {'timestamp': '2023-01-09', 'limit': '10'})
        ]
        
        for endpoint, params in endpoints:
            with patch('proxy_app.views.requests.Session.request') as mock_request:
                mock_request.return_value = self._mock_polygon_response({
                    "results": [],
                    "next_url": f"https://api.polygon.io/v3/{endpoint}?cursor=test&apikey=secret"
                })
                
                request = self._create_authenticated_request('GET', endpoint, params)
                response = self.view.get(request, endpoint)
                
                self.assertEqual(response.status_code, 200, f"Failed for endpoint: {endpoint}")
                if 'next_url' in response.data:
                    self.assertIn('api.dadosfinanceiros.com.br', response.data['next_url'])

    def test_cross_market_data_access(self):
        market_endpoints = [
            ('reference/tickers/', {'market': 'stocks'}),
            ('reference/tickers/', {'market': 'fx'}),
            ('reference/tickers/', {'market': 'crypto'}),
            ('reference/indices/', {}),
            ('conversion/USD/EUR/', {'amount': '100'})
        ]
        
        for endpoint, params in market_endpoints:
            with patch('proxy_app.views.requests.Session.request') as mock_request:
                mock_request.return_value = self._mock_polygon_response({"results": []})
                
                request = self._create_authenticated_request('GET', endpoint, params)
                response = self.view.get(request, endpoint)
                
                self.assertEqual(response.status_code, 200, f"Failed for endpoint: {endpoint}")

    def test_authentication_method_switching(self):
        endpoint = 'stocks/tickers/'
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            jwt_request = self._create_authenticated_request('GET', endpoint, use_jwt=True)
            jwt_response = self.view.get(jwt_request, endpoint)
            self.assertEqual(jwt_response.status_code, 200)
            
            token_request = self._create_authenticated_request('GET', endpoint, use_jwt=False)
            token_response = self.view.get(token_request, endpoint)
            self.assertEqual(token_response.status_code, 200)

    def test_daily_limit_across_endpoints(self):
        self.user.daily_request_limit = 3
        self.user.daily_requests_made = 0
        self.user.save()
        
        endpoints = ['stocks/tickers/', 'forex/EUR:USD/rates/', 'crypto/BTC:USD/trades/']
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            for i, endpoint in enumerate(endpoints):
                request = self._create_authenticated_request('GET', endpoint, use_jwt=False)
                response = self.view.get(request, endpoint)
                
                if i < 3:
                    self.assertEqual(response.status_code, 200)
                else:
                    self.assertEqual(response.status_code, 429)

    @override_settings(DEBUG=True)
    def test_debug_mode_security(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.side_effect = Exception("Test exception")
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertGreaterEqual(response.status_code, 500)
            
            response_content = json.dumps(response.data)
            self.assertNotIn(self.request_token, response_content)
            self.assertNotIn('apiKey', response_content)


class ErrorRecoveryTests(BaseProxyTestCase):

    def test_partial_service_degradation(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.side_effect = [
                requests.Timeout("First attempt failed"),
                self._mock_polygon_response({"results": []})
            ]
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 504)

    def test_service_recovery_after_failure(self):
        endpoint = 'stocks/tickers/'
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.side_effect = requests.ConnectionError("Service unavailable")
            
            request = self._create_authenticated_request('GET', endpoint)
            response = self.view.get(request, endpoint)
            self.assertEqual(response.status_code, 502)
            
            mock_request.side_effect = None
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            request = self._create_authenticated_request('GET', endpoint)
            response = self.view.get(request, endpoint)
            self.assertEqual(response.status_code, 200)

    def test_graceful_degradation_with_invalid_api_key(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response(
                {"error": "Invalid API key"}, 
                401
            )
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 401)
            self.assertIn('error', response.data)

    def test_handling_polygon_rate_limits(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response(
                {"error": "Rate limit exceeded"}, 
                429
            )
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            
            self.assertEqual(response.status_code, 429)

    def test_network_instability_simulation(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.side_effect = [
                requests.Timeout("Network timeout"),
                requests.ConnectionError("Connection reset"),
                self._mock_polygon_response({"results": []})
            ]
            
            for expected_status in [504, 502]:
                request = self._create_authenticated_request('GET', 'stocks/tickers/')
                response = self.view.get(request, 'stocks/tickers/')
                self.assertEqual(response.status_code, expected_status)
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            response = self.view.get(request, 'stocks/tickers/')
            self.assertEqual(response.status_code, 200)


class ConfigurationTests(BaseProxyTestCase):

    @override_settings(PROXY_TIMEOUT=1)
    def test_custom_timeout_setting(self):
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_request.return_value = self._mock_polygon_response({"results": []})
            
            request = self._create_authenticated_request('GET', 'stocks/tickers/')
            self.view.get(request, 'stocks/tickers/')
            
            args, kwargs = mock_request.call_args
            self.assertEqual(kwargs['timeout'], 1)

    @override_settings(PROXY_DOMAIN='custom.proxy.com')
    def test_custom_proxy_domain(self):
        test_data = {
            "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=test&apikey=secret"
        }
        
        request = self._create_authenticated_request('GET', 'stocks/tickers/')
        result = self.view._replace_polygon_urls(test_data, request)
        
        self.assertIn('custom.proxy.com', result["next_url"])

    def test_missing_polygon_api_key_handling(self):
        with override_settings(POLYGON_API_KEY=None):
            with patch('proxy_app.views.requests.Session.request') as mock_request:
                mock_request.return_value = self._mock_polygon_response({"results": []})
                
                request = self._create_authenticated_request('GET', 'stocks/tickers/')
                response = self.view.get(request, 'stocks/tickers/')
                
                args, kwargs = mock_request.call_args
                self.assertIsNone(kwargs['params'].get('apiKey'))

    def test_environment_variable_override(self):
        with override_settings(
            POLYGON_BASE_URL='https://custom.polygon.io',
            POLYGON_API_KEY='custom-api-key'
        ):
            view_instance = type(self.view)()
            view_instance._setup_configuration()
            
            self.assertEqual(view_instance.polygon_base_url, 'https://custom.polygon.io')
            self.assertEqual(view_instance.polygon_api_key, 'custom-api-key') 