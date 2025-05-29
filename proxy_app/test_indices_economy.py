import json
from unittest.mock import MagicMock, patch
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from proxy_app.test_comprehensive import BaseProxyTestCase
from proxy_app.views import PolygonProxyView
from users.models import User

User = get_user_model()


class IndicesEconomyEndpointTests(BaseProxyTestCase):

    @patch('proxy_app.views.requests.Session.request')
    def test_indices_endpoint(self, mock_request):
        mock_response_data = {
            "results": [
                {
                    "value": 4517.59,
                    "type": "indices",
                    "session": "regular",
                    "name": "S&P 500",
                    "timeframe": "1 day",
                    "market_status": "open",
                    "timestamp": 1673308800000
                }
            ],
            "status": "OK",
            "request_id": "test-indices-123"
        }
        
        mock_request.return_value = self._mock_polygon_response(mock_response_data)
        
        request = self._create_authenticated_request('GET', 'indices/stocks/')
        response = self.view.get(request, 'indices/stocks/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'S&P 500')
        
        # Verify status key removal
        self.assertNotIn('status', response.data)

    @patch('proxy_app.views.requests.Session.request')
    def test_economic_indicators_endpoint(self, mock_request):
        mock_response_data = {
            "results": [
                {
                    "type": "economic_indicator",
                    "name": "Consumer Price Index",
                    "value": 289.1,
                    "period": "monthly",
                    "date": "2023-01-01",
                    "unit": "index",
                    "seasonally_adjusted": True
                }
            ],
            "count": 1,
            "status": "OK",
            "next_url": "https://api.polygon.io/v1/indicators/cpi?cursor=next123&apikey=secret"
        }
        
        mock_request.return_value = self._mock_polygon_response(mock_response_data)
        
        request = self._create_authenticated_request('GET', 'indicators/cpi/', {
            'date': '2023-01-01'
        })
        
        response = self.view.get(request, 'indicators/cpi/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['results'][0]['name'], 'Consumer Price Index')
        
        # Verify URL replacement
        if 'next_url' in response.data:
            self.assertIn('api.dadosfinanceiros.com.br', response.data['next_url'])
            self.assertNotIn('apikey', response.data['next_url'])
        
        # Verify status key removal
        self.assertNotIn('status', response.data)

    @patch('proxy_app.views.requests.Session.request')
    def test_federal_funds_rate_endpoint(self, mock_request):
        mock_response_data = {
            "results": [
                {
                    "date": "2023-01-01",
                    "value": 4.75,
                    "type": "federal_funds_rate",
                    "period": "daily"
                }
            ],
            "count": 1,
            "status": "OK"
        }
        
        mock_request.return_value = self._mock_polygon_response(mock_response_data)
        
        request = self._create_authenticated_request('GET', 'fed/rates/', {
            'from_date': '2023-01-01',
            'to_date': '2023-01-31'
        })
        
        response = self.view.get(request, 'fed/rates/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['results'][0]['value'], 4.75)
        
        # Verify status key removal
        self.assertNotIn('status', response.data)

    @patch('proxy_app.views.requests.Session.request')
    def test_gdp_endpoint(self, mock_request):
        mock_response_data = {
            "results": [
                {
                    "date": "2023-Q1",
                    "value": 26950.0,
                    "type": "gdp",
                    "period": "quarterly",
                    "unit": "billions_usd",
                    "seasonally_adjusted": True
                }
            ],
            "status": "OK"
        }
        
        mock_request.return_value = self._mock_polygon_response(mock_response_data)
        
        request = self._create_authenticated_request('GET', 'indicators/gdp/', {
            'period': 'quarterly'
        })
        
        response = self.view.get(request, 'indicators/gdp/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['results'][0]['value'], 26950.0)
        
        # Verify status key removal
        self.assertNotIn('status', response.data)

    @patch('proxy_app.views.requests.Session.request')
    def test_unemployment_rate_endpoint(self, mock_request):
        mock_response_data = {
            "results": [
                {
                    "date": "2023-01-01",
                    "value": 3.4,
                    "type": "unemployment_rate",
                    "period": "monthly",
                    "unit": "percent",
                    "seasonally_adjusted": True
                }
            ],
            "status": "OK"
        }
        
        mock_request.return_value = self._mock_polygon_response(mock_response_data)
        
        request = self._create_authenticated_request('GET', 'indicators/unemployment/', {
            'date': '2023-01-01'
        })
        
        response = self.view.get(request, 'indicators/unemployment/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['results'][0]['value'], 3.4)
        
        # Verify status key removal
        self.assertNotIn('status', response.data)


class IndicesEndpointTests(BaseProxyTestCase):

    @patch('proxy_app.views.requests.Session.request')
    def test_all_indices_endpoint(self, mock_request):
        expected_response = {
            "results": [
                {
                    "ticker": "I:SPX",
                    "name": "S&P 500",
                    "market": "indices",
                    "locale": "us"
                },
                {
                    "ticker": "I:DJI",
                    "name": "Dow Jones Industrial Average",
                    "market": "indices",
                    "locale": "us"
                }
            ],
            "status": "OK",
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "next_url": "https://api.polygon.io/v3/reference/indices?cursor=YXA9MjAyMy0wMy0zMCZhcz1BQUEmb3JkZXI9YXNjJmxpbWl0PTEwJnNvcnQ9dGlja2Vy"
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'reference/indices/', {
            'market': 'indices',
            'order': 'asc',
            'limit': '10',
            'sort': 'ticker'
        })
        
        response = self.view.get(request, 'reference/indices/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertEqual(len(response_data['results']), 2)
        self.assertEqual(response_data['results'][0]['ticker'], 'I:SPX')
        self.assertEqual(response_data['results'][0]['name'], 'S&P 500')
        self.assertIn('next_url', response_data)
        self.assertIn('api.dadosfinanceiros.com.br', response_data['next_url'])
        
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertIn('v3/reference/indices', kwargs['url'])

    @patch('proxy_app.views.requests.Session.request')
    def test_index_details_endpoint(self, mock_request):
        expected_response = {
            "results": {
                "ticker": "I:SPX",
                "name": "S&P 500",
                "market": "indices",
                "locale": "us"
            },
            "status": "OK",
            "request_id": "6a7e466b6837652eca4def2f7b7adc56"
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'reference/indices/I:SPX/')
        response = self.view.get(request, 'reference/indices/I:SPX/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertEqual(response_data['results']['ticker'], 'I:SPX')
        self.assertEqual(response_data['results']['name'], 'S&P 500')
        self.assertEqual(response_data['results']['market'], 'indices')
        
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertIn('v3/reference/indices/I:SPX', kwargs['url'])

    @patch('proxy_app.views.requests.Session.request')
    def test_index_aggregates_endpoint(self, mock_request):
        expected_response = {
            "ticker": "I:SPX",
            "adjusted": True,
            "queryCount": 5,
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "resultsCount": 5,
            "status": "OK",
            "results": [
                {
                    "v": 1000000,
                    "vw": 4200.5,
                    "o": 4195.2,
                    "c": 4205.8,
                    "h": 4210.3,
                    "l": 4190.1,
                    "t": 1672704000000,
                    "n": 500
                }
            ]
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'indices/I:SPX/aggregates/', {
            'multiplier': '1',
            'timespan': 'day',
            'from_date': '2023-01-01',
            'to_date': '2023-01-10'
        })
        
        response = self.view.get(request, 'indices/I:SPX/aggregates/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertEqual(response_data['ticker'], 'I:SPX')
        self.assertIn('results', response_data)
        self.assertEqual(len(response_data['results']), 1)


class EconomyEndpointTests(BaseProxyTestCase):

    @patch('proxy_app.views.requests.Session.request')
    def test_treasury_yields_endpoint(self, mock_request):
        expected_response = {
            "results": {
                "US10Y": [
                    {
                        "date": "2023-01-03",
                        "value": 3.79
                    },
                    {
                        "date": "2023-01-04",
                        "value": 3.68
                    },
                    {
                        "date": "2023-01-05",
                        "value": 3.75
                    }
                ]
            },
            "status": "OK",
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "next_url": "https://api.polygon.io/v1/indicators/treasury-yields?cursor=YXA9MjAyMy0wMy0zMCZhcz1BQUEmb3JkZXI9YXNjJmxpbWl0PTEwJnNvcnQ9ZGF0ZQ"
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'indicators/treasury-yields/', {
            'ticker': 'US10Y',
            'from': '2023-01-01',
            'to': '2023-01-31',
            'order': 'asc',
            'limit': '10'
        })
        
        response = self.view.get(request, 'indicators/treasury-yields/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertIn('US10Y', response_data['results'])
        self.assertEqual(len(response_data['results']['US10Y']), 3)
        self.assertEqual(response_data['results']['US10Y'][0]['date'], '2023-01-03')
        self.assertEqual(response_data['results']['US10Y'][0]['value'], 3.79)
        self.assertIn('next_url', response_data)
        self.assertIn('api.dadosfinanceiros.com.br', response_data['next_url'])
        
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertIn('v1/indicators/treasury-yields', kwargs['url'])

    @patch('proxy_app.views.requests.Session.request')
    def test_fed_yields_direct_endpoint(self, mock_request):
        expected_response = {
            "results": [
                {
                    "date": "2023-01-03",
                    "value": 3.79,
                    "maturity": "10Y"
                },
                {
                    "date": "2023-01-04", 
                    "value": 3.68,
                    "maturity": "10Y"
                }
            ],
            "status": "OK",
            "request_id": "6a7e466b6837652eca4def2f7b7adc56"
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'fed/treasury-yields/', {
            'maturity': '10Y',
            'date.gte': '2023-01-01'
        })
        
        response = self.view.get(request, 'fed/treasury-yields/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertEqual(len(response_data['results']), 2)
        
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        # Fed endpoints go directly to polygon without version prefix
        self.assertIn('fed/treasury-yields', kwargs['url'])
        self.assertNotIn('/v1/', kwargs['url'])
        self.assertNotIn('/v2/', kwargs['url'])
        self.assertNotIn('/v3/', kwargs['url'])


class PartnersEndpointTests(BaseProxyTestCase):

    @patch('proxy_app.views.requests.Session.request')
    def test_benzinga_analyst_ratings_endpoint(self, mock_request):
        expected_response = {
            "status": "OK",
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "results": {
                "analysts": [
                    {
                        "name": "John Smith",
                        "company": "Example Securities",
                        "rating": "Buy",
                        "price_target": 200,
                        "timestamp": "2023-01-15T09:30:00Z",
                        "action": "Reiterated"
                    },
                    {
                        "name": "Jane Doe",
                        "company": "Sample Investments", 
                        "rating": "Overweight",
                        "price_target": 210,
                        "timestamp": "2023-01-10T14:00:00Z",
                        "action": "Upgraded"
                    }
                ]
            }
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'meta/symbols/AAPL/analysts/')
        response = self.view.get(request, 'meta/symbols/AAPL/analysts/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertIn('analysts', response_data['results'])
        self.assertEqual(len(response_data['results']['analysts']), 2)
        self.assertEqual(response_data['results']['analysts'][0]['name'], 'John Smith')
        self.assertEqual(response_data['results']['analysts'][0]['rating'], 'Buy')
        
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertIn('v1/meta/symbols/AAPL/analysts', kwargs['url'])

    @patch('proxy_app.views.requests.Session.request')
    def test_benzinga_company_endpoint(self, mock_request):
        expected_response = {
            "logo": "https://s3.polygon.io/logos/aapl/logo.png",
            "exchange": "Nasdaq Global Select",
            "name": "Apple Inc.",
            "symbol": "AAPL",
            "listdate": "1980-12-12",
            "cik": "0000320193",
            "bloomberg": "EQ0010169500001000",
            "figi": "BBG000B9XRY4",
            "lei": "HWUPKR0MPOU8FGXBT394",
            "sic": 3571,
            "country": "us",
            "industry": "Computer Hardware",
            "sector": "Technology",
            "marketcap": 2952828995000,
            "employees": 154000,
            "phone": "+14089961010",
            "ceo": "Timothy D. Cook",
            "url": "http://www.apple.com",
            "description": "Apple Inc. designs, manufactures, and markets smartphones...",
            "similar": [
                "MSFT", "AAPL", "AMZN", "GOOGL", "FB", "TSLA", "NVDA", "PYPL", "INTC", "CMCSA"
            ],
            "tags": [
                "Technology", "Consumer Electronics", "Computer Hardware"
            ],
            "updated": "2023-03-30"
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'meta/symbols/AAPL/company/')
        response = self.view.get(request, 'meta/symbols/AAPL/company/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        # Note: This endpoint doesn't have "status" field in response
        self.assertEqual(response_data['symbol'], 'AAPL')
        self.assertEqual(response_data['name'], 'Apple Inc.')
        self.assertIn('similar', response_data)
        self.assertIn('tags', response_data)
        
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertIn('v1/meta/symbols/AAPL/company', kwargs['url'])


class AdvancedForexEndpointTests(BaseProxyTestCase):

    @patch('proxy_app.views.requests.Session.request')
    def test_forex_aggregates_endpoint(self, mock_request):
        expected_response = {
            "ticker": "C:EURUSD",
            "adjusted": True,
            "queryCount": 5,
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "resultsCount": 5,
            "status": "OK",
            "results": [
                {
                    "v": 1000000,
                    "vw": 1.0845,
                    "o": 1.0842,
                    "c": 1.0847,
                    "h": 1.0850,
                    "l": 1.0840,
                    "t": 1672704000000
                }
            ]
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'forex/C:EURUSD/aggregates/', {
            'multiplier': '1',
            'timespan': 'hour',
            'from_date': '2023-01-01',
            'to_date': '2023-01-02'
        })
        
        response = self.view.get(request, 'forex/C:EURUSD/aggregates/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertEqual(response_data['ticker'], 'C:EURUSD')
        self.assertIn('results', response_data)

    @patch('proxy_app.views.requests.Session.request')
    def test_forex_real_time_quote_endpoint(self, mock_request):
        expected_response = {
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "status": "OK",
            "results": {
                "T": "C:EURUSD",
                "a": 1.0847,
                "b": 1.0845,
                "c": [1],
                "f": 1673271000000000000,
                "i": [1],
                "p": 1.0846,
                "q": 1673271000000000000,
                "t": 1673271000000000000,
                "x": 1,
                "y": 1673271000000000000
            }
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'last/currencies/C:EURUSD/')
        response = self.view.get(request, 'last/currencies/C:EURUSD/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertEqual(response_data['results']['T'], 'C:EURUSD')

    @patch('proxy_app.views.requests.Session.request')
    def test_forex_historical_rates_endpoint(self, mock_request):
        expected_response = {
            "results": [
                {
                    "ask": 1.0850,
                    "bid": 1.0848,
                    "exchange": 1,
                    "timestamp": 1673271000000
                },
                {
                    "ask": 1.0855,
                    "bid": 1.0853,
                    "exchange": 1,
                    "timestamp": 1673271060000
                }
            ],
            "status": "OK",
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "next_url": "https://api.polygon.io/v3/quotes/C:EURUSD?cursor=YXNjLmMxLjE2NzMyNzEwMDAwMDAwMDAwMDAuMS4x"
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'forex/C:EURUSD/quotes/', {
            'timestamp': '2023-01-09',
            'order': 'asc',
            'limit': '10'
        })
        
        response = self.view.get(request, 'forex/C:EURUSD/quotes/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertEqual(len(response_data['results']), 2)
        self.assertIn('next_url', response_data)
        self.assertIn('api.dadosfinanceiros.com.br', response_data['next_url'])


class CryptoAdvancedEndpointTests(BaseProxyTestCase):

    @patch('proxy_app.views.requests.Session.request')
    def test_crypto_aggregates_endpoint(self, mock_request):
        expected_response = {
            "ticker": "X:BTCUSD",
            "adjusted": True,
            "queryCount": 24,
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "resultsCount": 24,
            "status": "OK",
            "results": [
                {
                    "v": 150000000,
                    "vw": 42500.75,
                    "o": 42450.00,
                    "c": 42600.25,
                    "h": 42750.50,
                    "l": 42300.00,
                    "t": 1672704000000
                }
            ]
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'crypto/X:BTCUSD/aggregates/', {
            'multiplier': '1',
            'timespan': 'hour',
            'from_date': '2023-01-01',
            'to_date': '2023-01-02'
        })
        
        response = self.view.get(request, 'crypto/X:BTCUSD/aggregates/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertEqual(response_data['ticker'], 'X:BTCUSD')
        self.assertIn('results', response_data)
        self.assertEqual(len(response_data['results']), 1)

    @patch('proxy_app.views.requests.Session.request')
    def test_crypto_trades_endpoint(self, mock_request):
        expected_response = {
            "results": [
                {
                    "conditions": [1],
                    "exchange": 1,
                    "price": 42600.25,
                    "sip_timestamp": 1673271000000000000,
                    "size": 0.05,
                    "timestamp": 1673271000000000000
                },
                {
                    "conditions": [1],
                    "exchange": 1,
                    "price": 42610.00,
                    "sip_timestamp": 1673271060000000000,
                    "size": 0.1,
                    "timestamp": 1673271060000000000
                }
            ],
            "status": "OK",
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "next_url": "https://api.polygon.io/v3/trades/X:BTCUSD?cursor=YXNjLmMxLjE2NzMyNzEwMDAwMDAwMDAwMDAuMS4x"
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'crypto/X:BTCUSD/trades/', {
            'timestamp': '2023-01-09',
            'order': 'asc',
            'limit': '10'
        })
        
        response = self.view.get(request, 'crypto/X:BTCUSD/trades/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertEqual(len(response_data['results']), 2)
        self.assertIn('next_url', response_data)
        self.assertIn('api.dadosfinanceiros.com.br', response_data['next_url'])

    @patch('proxy_app.views.requests.Session.request')
    def test_crypto_snapshot_endpoint(self, mock_request):
        expected_response = {
            "status": "OK",
            "request_id": "6a7e466b6837652eca4def2f7b7adc56",
            "results": [
                {
                    "ticker": "X:BTCUSD",
                    "type": "crypto",
                    "session": {
                        "change": 150.25,
                        "change_percent": 0.35,
                        "close": 42600.25,
                        "high": 42750.50,
                        "low": 42300.00,
                        "open": 42450.00,
                        "volume": 150000000,
                        "previous_close": 42450.00
                    },
                    "last_quote": {
                        "ask": 42602.00,
                        "ask_size": 0.5,
                        "bid": 42598.00,
                        "bid_size": 0.5,
                        "timestamp": "2023-05-19T20:00:00Z"
                    },
                    "last_trade": {
                        "conditions": [1],
                        "price": 42600.25,
                        "size": 0.05,
                        "timestamp": "2023-05-19T20:00:00Z",
                        "exchange": 1
                    }
                }
            ]
        }
        
        mock_request.return_value = self._mock_polygon_response(expected_response)
        
        request = self._create_authenticated_request('GET', 'snapshot/crypto/', {
            'ticker.any_of': 'X:BTCUSD,X:ETHUSD'
        })
        
        response = self.view.get(request, 'snapshot/crypto/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        
        self.assertNotIn('status', response_data)
        self.assertIn('results', response_data)
        self.assertEqual(response_data['results'][0]['ticker'], 'X:BTCUSD')
        self.assertEqual(response_data['results'][0]['type'], 'crypto')


class ComplexPaginationTests(BaseProxyTestCase):

    def test_complex_url_replacement_with_multiple_params(self):
        test_data = {
            "count": 100,
            "next_url": "https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=asc&limit=100&cursor=YXNjLmMxLjE2NzMyNzEwMDAwMDAwMDAwMDAuMS4x&apikey=secret123",
            "previous_url": "https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=asc&limit=100&cursor=prev456&apikey=secret123",
            "results": []
        }
        
        request = self._create_authenticated_request('GET', 'reference/tickers/')
        result = self.view._replace_polygon_urls(test_data, request)
        
        expected_next = "https://api.dadosfinanceiros.com.br/v1/reference/tickers?market=stocks&active=true&order=asc&limit=100&cursor=YXNjLmMxLjE2NzMyNzEwMDAwMDAwMDAwMDAuMS4x"
        expected_prev = "https://api.dadosfinanceiros.com.br/v1/reference/tickers?market=stocks&active=true&order=asc&limit=100&cursor=prev456"
        
        self.assertEqual(result["next_url"], expected_next)
        self.assertEqual(result["previous_url"], expected_prev)
        self.assertNotIn('apikey', result["next_url"])
        self.assertNotIn('apikey', result["previous_url"])

    def test_url_replacement_preserves_query_params(self):
        test_data = {
            "next_url": "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2023-01-01/2023-01-10?adjusted=true&sort=asc&limit=120&cursor=test123&apikey=secret"
        }
        
        request = self._create_authenticated_request('GET', 'stocks/AAPL/aggregates/')
        result = self.view._replace_polygon_urls(test_data, request)
        
        expected_url = "https://api.dadosfinanceiros.com.br/v1/aggs/ticker/AAPL/range/1/day/2023-01-01/2023-01-10?adjusted=true&sort=asc&limit=120&cursor=test123"
        self.assertEqual(result["next_url"], expected_url)

    def test_url_replacement_handles_apikey_in_different_positions(self):
        test_cases = [
            "https://api.polygon.io/v3/tickers?apikey=secret&market=stocks",
            "https://api.polygon.io/v3/tickers?market=stocks&apikey=secret",
            "https://api.polygon.io/v3/tickers?market=stocks&apikey=secret&active=true",
            "https://api.polygon.io/v3/tickers?apikey=secret"
        ]
        
        for url in test_cases:
            test_data = {"next_url": url}
            request = self._create_authenticated_request('GET', 'reference/tickers/')
            result = self.view._replace_polygon_urls(test_data, request)
            
            self.assertNotIn('apikey', result["next_url"])
            self.assertIn('api.dadosfinanceiros.com.br', result["next_url"])
            self.assertIn('/v1/', result["next_url"]) 