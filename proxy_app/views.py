import json
import requests
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlencode, urlparse

from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views import View
from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission

logger = logging.getLogger(__name__)


def get_permission_classes():
    if getattr(settings, 'ENV', 'local') == "local":
        return [AllowAny]
    return [IsAuthenticated, DailyLimitPermission]


def get_authentication_classes():
    if getattr(settings, 'ENV', 'local') == "local":
        return []
    return [JWTAuthentication, RequestTokenAuthentication]


_permissions = get_permission_classes()
_authentications = get_authentication_classes()


@permission_classes(_permissions)
def api_documentation(request):
    return render(request, "api/docs.html")


class UnifiedFinancialAPIView(APIView):
    """
    Unified Financial Data API Proxy
    Routes ALL requests to optimal provider (Polygon.io or FMP Ultimate)
    Maintains /api/v1/ structure regardless of backend provider
    """
    
    renderer_classes = [JSONRenderer]
    authentication_classes = _authentications
    permission_classes = _permissions
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # API Configuration
        self.fmp_api_key = getattr(settings, 'FMP_API_KEY', 'your-fmp-api-key-here')
        self.polygon_api_key = getattr(settings, 'POLYGON_API_KEY', 'your-polygon-api-key-here')
        self.fmp_base_url = getattr(settings, 'FMP_BASE_URL', 'https://financialmodelingprep.com/api')
        self.polygon_base_url = getattr(settings, 'POLYGON_BASE_URL', 'https://api.polygon.io')
        
        # Complete endpoint mapping
        self.endpoint_mappings = self._initialize_endpoint_mappings()
        
        # Rate limiting
        self.rate_limits = {
            'fmp': {'calls': 3000, 'period': 60},
            'polygon': {'calls': 1000, 'period': 60}
        }
        
        # Cache TTL settings
        self.cache_ttl = {
            'real_time': 30,
            'intraday': 300,
            'daily': 3600,
            'fundamental': 86400,
            'news': 1800,
            'static': 604800
        }
        
        # Initialize requests session
        self.session = requests.Session()
        self.timeout = getattr(settings, 'PROXY_TIMEOUT', 30)
        self.proxy_domain = getattr(settings, 'PROXY_DOMAIN', 'api.dadosfinanceiros.com.br')

        # Environment-based authentication
        if getattr(settings, 'ENV', 'local') == "local":
            self.authentication_classes = []
            self.permission_classes = [AllowAny]

    def _initialize_endpoint_mappings(self) -> Dict[str, Dict]:
        """Initialize complete endpoint mapping configuration"""
        return {
            # Reference Data Endpoints
            'reference/tickers': {
                'provider': 'fmp',
                'endpoint': '/v3/stock/list',
                'method': 'GET',
                'cache_type': 'static'
            },
            'reference/ticker/{symbol}': {
                'provider': 'fmp',
                'endpoint': '/v3/profile/{symbol}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'reference/ticker/{symbol}/profile': {
                'provider': 'fmp',
                'endpoint': '/v3/profile/{symbol}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'reference/ticker/{symbol}/executives': {
                'provider': 'fmp',
                'endpoint': '/v3/key-executives/{symbol}',
                'method': 'GET',
                'cache_type': 'static'
            },
            'reference/ticker/{symbol}/peers': {
                'provider': 'fmp',
                'endpoint': '/v3/stock_peers',
                'method': 'GET',
                'cache_type': 'daily',
                'params_map': {'symbol': 'symbol'}
            },
            'reference/exchanges': {
                'provider': 'fmp',
                'endpoint': '/v3/exchanges-list',
                'method': 'GET',
                'cache_type': 'static'
            },
            'reference/market-status': {
                'provider': 'fmp',
                'endpoint': '/v3/is-the-market-open',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            
            # Market Data Endpoints
            'quotes/{symbol}': {
                'provider': 'fmp',
                'endpoint': '/v3/quote/{symbol}',
                'method': 'GET',
                'cache_type': 'real_time',
                'polygon_fallback': '/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}'
            },
            'quotes/batch': {
                'provider': 'fmp',
                'endpoint': '/v3/quote/{symbols}',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'quotes/gainers': {
                'provider': 'fmp',
                'endpoint': '/v3/gainers',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'quotes/losers': {
                'provider': 'fmp',
                'endpoint': '/v3/losers',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'quotes/active': {
                'provider': 'fmp',
                'endpoint': '/v3/actives',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            
            # Historical Data Endpoints
            'historical/{symbol}': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-price-full/{symbol}',
                'method': 'GET',
                'cache_type': 'daily',
                'polygon_fallback': '/v2/aggs/ticker/{symbol}/range/1/day/{from}/{to}'
            },
            'historical/{symbol}/intraday': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-chart/{interval}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday'
            },
            'historical/{symbol}/splits': {
                'provider': 'fmp',
                'endpoint': '/v3/stock_split_calendar',
                'method': 'GET',
                'cache_type': 'daily',
                'polygon_fallback': '/v3/reference/splits'
            },
            'historical/{symbol}/dividends': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-price-full/stock_dividend/{symbol}',
                'method': 'GET',
                'cache_type': 'daily',
                'polygon_fallback': '/v3/reference/dividends'
            },
            
            # Tick-level Data (Polygon.io exclusive)
            'ticks/{symbol}/trades': {
                'provider': 'polygon',
                'endpoint': '/v3/trades/{symbol}',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'ticks/{symbol}/quotes': {
                'provider': 'polygon',
                'endpoint': '/v3/quotes/{symbol}',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'ticks/{symbol}/aggregates': {
                'provider': 'polygon',
                'endpoint': '/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}',
                'method': 'GET',
                'cache_type': 'intraday'
            },
            
            # Options Data (Polygon.io exclusive)
            'options/contracts': {
                'provider': 'polygon',
                'endpoint': '/v3/reference/options/contracts',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'options/chain/{symbol}': {
                'provider': 'polygon',
                'endpoint': '/v3/snapshot/options/{symbol}',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'options/{symbol}/snapshot': {
                'provider': 'polygon',
                'endpoint': '/v3/snapshot/options/{symbol}',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'options/{contract}/details': {
                'provider': 'polygon',
                'endpoint': '/v3/reference/options/contracts/{contract}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'options/{contract}/historical': {
                'provider': 'polygon',
                'endpoint': '/v2/aggs/ticker/{contract}/range/{multiplier}/{timespan}/{from}/{to}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            
            # Futures Data (Polygon.io exclusive)
            'futures/contracts': {
                'provider': 'polygon',
                'endpoint': '/v3/reference/futures/contracts',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'futures/{symbol}/snapshot': {
                'provider': 'polygon',
                'endpoint': '/v2/snapshot/locale/global/markets/futures/tickers/{symbol}',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'futures/{symbol}/historical': {
                'provider': 'polygon',
                'endpoint': '/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            
            # Forex Data
            'forex/rates': {
                'provider': 'fmp',
                'endpoint': '/v3/fx',
                'method': 'GET',
                'cache_type': 'real_time',
                'polygon_fallback': '/v1/last/currencies/{from}/{to}'
            },
            'forex/{pair}/historical': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-price-full/{pair}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'forex/{pair}/intraday': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-chart/{interval}/{pair}',
                'method': 'GET',
                'cache_type': 'intraday'
            },
            
            # Cryptocurrency Data
            'crypto/prices': {
                'provider': 'fmp',
                'endpoint': '/v3/cryptocurrencies',
                'method': 'GET',
                'cache_type': 'real_time',
                'polygon_fallback': '/v1/last/crypto/{from}/{to}'
            },
            'crypto/{symbol}/historical': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-price-full/{symbol}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'crypto/{symbol}/intraday': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-chart/{interval}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday'
            },
            
            # Fundamental Data (FMP exclusive)
            'fundamentals/{symbol}/income-statement': {
                'provider': 'fmp',
                'endpoint': '/v3/income-statement/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'fundamentals/{symbol}/balance-sheet': {
                'provider': 'fmp',
                'endpoint': '/v3/balance-sheet-statement/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'fundamentals/{symbol}/cash-flow': {
                'provider': 'fmp',
                'endpoint': '/v3/cash-flow-statement/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'fundamentals/{symbol}/ratios': {
                'provider': 'fmp',
                'endpoint': '/v3/ratios/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'fundamentals/{symbol}/metrics': {
                'provider': 'fmp',
                'endpoint': '/v3/key-metrics/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'fundamentals/{symbol}/growth': {
                'provider': 'fmp',
                'endpoint': '/v3/financial-growth/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            
            # Valuation Data (FMP exclusive)
            'valuation/{symbol}/dcf': {
                'provider': 'fmp',
                'endpoint': '/v3/discounted-cash-flow/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'valuation/{symbol}/ratios': {
                'provider': 'fmp',
                'endpoint': '/v3/ratios-ttm/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'valuation/{symbol}/enterprise-value': {
                'provider': 'fmp',
                'endpoint': '/v3/enterprise-values/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'valuation/screener': {
                'provider': 'fmp',
                'endpoint': '/v3/stock-screener',
                'method': 'GET',
                'cache_type': 'daily'
            },
            
            # News & Sentiment (FMP exclusive)
            'news': {
                'provider': 'fmp',
                'endpoint': '/v3/stock_news',
                'method': 'GET',
                'cache_type': 'news'
            },
            'news/{symbol}': {
                'provider': 'fmp',
                'endpoint': '/v3/stock_news',
                'method': 'GET',
                'cache_type': 'news',
                'params_map': {'symbol': 'tickers'}
            },
            'news/sentiment/{symbol}': {
                'provider': 'fmp',
                'endpoint': '/v4/sentiment-analysis',
                'method': 'GET',
                'cache_type': 'news'
            },
            'news/press-releases/{symbol}': {
                'provider': 'fmp',
                'endpoint': '/v3/press-releases/{symbol}',
                'method': 'GET',
                'cache_type': 'news'
            },
            
            # Analyst Data (FMP exclusive)
            'analysts/{symbol}/estimates': {
                'provider': 'fmp',
                'endpoint': '/v3/analyst-estimates/{symbol}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'analysts/{symbol}/recommendations': {
                'provider': 'fmp',
                'endpoint': '/v3/analyst-stock-recommendations/{symbol}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'analysts/{symbol}/price-targets': {
                'provider': 'fmp',
                'endpoint': '/v4/price-target/{symbol}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'analysts/{symbol}/upgrades-downgrades': {
                'provider': 'fmp',
                'endpoint': '/v4/upgrades-downgrades/{symbol}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            
            # Earnings Data (FMP exclusive)
            'earnings/{symbol}/calendar': {
                'provider': 'fmp',
                'endpoint': '/v3/earning_calendar',
                'method': 'GET',
                'cache_type': 'daily',
                'params_map': {'symbol': 'symbol'}
            },
            'earnings/{symbol}/history': {
                'provider': 'fmp',
                'endpoint': '/v3/historical/earning_calendar/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'earnings/{symbol}/surprises': {
                'provider': 'fmp',
                'endpoint': '/v3/earnings-surprises/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'earnings/{symbol}/transcripts': {
                'provider': 'fmp',
                'endpoint': '/v4/batch_earning_call_transcript/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'earnings/calendar': {
                'provider': 'fmp',
                'endpoint': '/v3/earning_calendar',
                'method': 'GET',
                'cache_type': 'daily'
            },
            
            # Institutional Data (FMP exclusive)
            'institutional/{symbol}/holdings': {
                'provider': 'fmp',
                'endpoint': '/v3/institutional-holder/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'institutional/{symbol}/13f': {
                'provider': 'fmp',
                'endpoint': '/v3/form-thirteen/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'institutional/funds/{cik}': {
                'provider': 'fmp',
                'endpoint': '/v3/form-thirteen/{cik}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            
            # Insider Trading (FMP exclusive)
            'insider/{symbol}/transactions': {
                'provider': 'fmp',
                'endpoint': '/v4/insider-trading',
                'method': 'GET',
                'cache_type': 'daily',
                'params_map': {'symbol': 'symbol'}
            },
            'insider/{symbol}/ownership': {
                'provider': 'fmp',
                'endpoint': '/v3/insider-trading/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            
            # Economic Data (FMP exclusive)
            'economy/gdp': {
                'provider': 'fmp',
                'endpoint': '/v4/economic',
                'method': 'GET',
                'cache_type': 'fundamental',
                'static_params': {'name': 'GDP'}
            },
            'economy/inflation': {
                'provider': 'fmp',
                'endpoint': '/v4/economic',
                'method': 'GET',
                'cache_type': 'fundamental',
                'static_params': {'name': 'CPI'}
            },
            'economy/unemployment': {
                'provider': 'fmp',
                'endpoint': '/v4/economic',
                'method': 'GET',
                'cache_type': 'fundamental',
                'static_params': {'name': 'unemploymentRate'}
            },
            'economy/interest-rates': {
                'provider': 'fmp',
                'endpoint': '/v4/economic',
                'method': 'GET',
                'cache_type': 'fundamental',
                'static_params': {'name': 'federalFundsRate'}
            },
            'economy/treasury-rates': {
                'provider': 'fmp',
                'endpoint': '/v4/treasury',
                'method': 'GET',
                'cache_type': 'daily'
            },
            
            # Technical Analysis
            'technical/{symbol}/sma': {
                'provider': 'fmp',
                'endpoint': '/v3/technical_indicator/{timespan}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday',
                'static_params': {'type': 'SMA'},
                'polygon_fallback': '/v1/indicators/sma/{symbol}'
            },
            'technical/{symbol}/ema': {
                'provider': 'fmp',
                'endpoint': '/v3/technical_indicator/{timespan}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday',
                'static_params': {'type': 'EMA'},
                'polygon_fallback': '/v1/indicators/ema/{symbol}'
            },
            'technical/{symbol}/rsi': {
                'provider': 'fmp',
                'endpoint': '/v3/technical_indicator/{timespan}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday',
                'static_params': {'type': 'RSI'},
                'polygon_fallback': '/v1/indicators/rsi/{symbol}'
            },
            'technical/{symbol}/macd': {
                'provider': 'fmp',
                'endpoint': '/v3/technical_indicator/{timespan}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday',
                'static_params': {'type': 'MACD'},
                'polygon_fallback': '/v1/indicators/macd/{symbol}'
            },
            'technical/{symbol}/bollinger-bands': {
                'provider': 'fmp',
                'endpoint': '/v3/technical_indicator/{timespan}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday',
                'static_params': {'type': 'BBANDS'}
            },
            'technical/{symbol}/stochastic': {
                'provider': 'fmp',
                'endpoint': '/v3/technical_indicator/{timespan}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday',
                'static_params': {'type': 'STOCH'}
            },
            'technical/{symbol}/adx': {
                'provider': 'fmp',
                'endpoint': '/v3/technical_indicator/{timespan}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday',
                'static_params': {'type': 'ADX'}
            },
            'technical/{symbol}/williams-r': {
                'provider': 'fmp',
                'endpoint': '/v3/technical_indicator/{timespan}/{symbol}',
                'method': 'GET',
                'cache_type': 'intraday',
                'static_params': {'type': 'WILLR'}
            },
            
            # SEC Filings (FMP exclusive)
            'sec/{symbol}/filings': {
                'provider': 'fmp',
                'endpoint': '/v3/sec_filings/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'sec/{symbol}/10k': {
                'provider': 'fmp',
                'endpoint': '/v3/sec_filings/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental',
                'static_params': {'type': '10-K'}
            },
            'sec/{symbol}/10q': {
                'provider': 'fmp',
                'endpoint': '/v3/sec_filings/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental',
                'static_params': {'type': '10-Q'}
            },
            'sec/{symbol}/8k': {
                'provider': 'fmp',
                'endpoint': '/v3/sec_filings/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental',
                'static_params': {'type': '8-K'}
            },
            'sec/rss-feed': {
                'provider': 'fmp',
                'endpoint': '/v4/rss_feed',
                'method': 'GET',
                'cache_type': 'news'
            },
            
            # ETF & Mutual Funds (FMP exclusive)
            'etf/list': {
                'provider': 'fmp',
                'endpoint': '/v3/etf/list',
                'method': 'GET',
                'cache_type': 'static'
            },
            'etf/{symbol}/holdings': {
                'provider': 'fmp',
                'endpoint': '/v3/etf-holder/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'etf/{symbol}/performance': {
                'provider': 'fmp',
                'endpoint': '/v3/etf-info',
                'method': 'GET',
                'cache_type': 'daily',
                'params_map': {'symbol': 'symbol'}
            },
            'funds/list': {
                'provider': 'fmp',
                'endpoint': '/v3/mutual-fund/list',
                'method': 'GET',
                'cache_type': 'static'
            },
            'funds/{symbol}/holdings': {
                'provider': 'fmp',
                'endpoint': '/v3/mutual-fund-holder/{symbol}',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            
            # Commodities (FMP exclusive)
            'commodities/metals': {
                'provider': 'fmp',
                'endpoint': '/v3/commodities',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'commodities/energy': {
                'provider': 'fmp',
                'endpoint': '/v3/commodities',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'commodities/agriculture': {
                'provider': 'fmp',
                'endpoint': '/v3/commodities',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'commodities/{symbol}/historical': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-price-full/{symbol}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            
            # Indices
            'indices/list': {
                'provider': 'fmp',
                'endpoint': '/v3/quotes/index',
                'method': 'GET',
                'cache_type': 'real_time',
                'polygon_fallback': '/v2/snapshot/locale/global/markets/indices'
            },
            'indices/{symbol}/historical': {
                'provider': 'fmp',
                'endpoint': '/v3/historical-price-full/{symbol}',
                'method': 'GET',
                'cache_type': 'daily',
                'polygon_fallback': '/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}'
            },
            'indices/{symbol}/components': {
                'provider': 'fmp',
                'endpoint': '/v3/sp500_constituent',
                'method': 'GET',
                'cache_type': 'static'
            },
            
            # Bulk Data (FMP exclusive)
            'bulk/eod/{date}': {
                'provider': 'fmp',
                'endpoint': '/v4/batch-request-end-of-day-prices',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'bulk/fundamentals/{date}': {
                'provider': 'fmp',
                'endpoint': '/v4/batch-request-financial-statements',
                'method': 'GET',
                'cache_type': 'fundamental'
            },
            'bulk/insider-trading/{date}': {
                'provider': 'fmp',
                'endpoint': '/v4/insider-trading',
                'method': 'GET',
                'cache_type': 'daily'
            },
            
            # Legacy Polygon.io endpoints for backward compatibility
            'snapshot': {
                'provider': 'polygon',
                'endpoint': '/v2/snapshot/locale/us/markets/stocks/tickers',
                'method': 'GET',
                'cache_type': 'real_time'
            },
            'aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}': {
                'provider': 'polygon',
                'endpoint': '/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}',
                'method': 'GET',
                'cache_type': 'daily'
            },
            'reference/tickers/{ticker}': {
                'provider': 'polygon',
                'endpoint': '/v3/reference/tickers/{ticker}',
                'method': 'GET',
                'cache_type': 'static'
            }
        }

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, path="", *args, **kwargs):
        """Handle all GET requests for financial data"""
        return self._handle_request(request, path, 'GET')

    def post(self, request, path="", *args, **kwargs):
        """Handle all POST requests for financial data"""
        return self._handle_request(request, path, 'POST')

    def put(self, request, path="", *args, **kwargs):
        """Handle all PUT requests for financial data"""
        return self._handle_request(request, path, 'PUT')

    def delete(self, request, path="", *args, **kwargs):
        """Handle all DELETE requests for financial data"""
        return self._handle_request(request, path, 'DELETE')

    def _handle_request(self, request, path, method):
        """Central request handler"""
        try:
            # Clean the path
            unified_path = self._extract_unified_path(path)
            
            # Find matching endpoint configuration
            endpoint_config = self._match_endpoint(unified_path)
            if not endpoint_config:
                return JsonResponse({
                    'error': 'Endpoint not found',
                    'path': unified_path,
                    'available_endpoints': list(self.endpoint_mappings.keys())[:10]  # Show first 10
                }, status=404)
            
            # Check rate limits
            provider = endpoint_config['provider']
            if not self._check_rate_limit(provider):
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'provider': provider
                }, status=429)
            
            # Check cache for GET requests
            if method == 'GET':
                cache_key = self._generate_cache_key(unified_path, request.GET)
                cached_response = cache.get(cache_key)
                if cached_response:
                    logger.info(f"Cache hit for {cache_key}")
                    return JsonResponse(cached_response)
            
            # Route request to provider
            response_data = self._route_request(endpoint_config, unified_path, request)
            
            # Transform response to unified format
            unified_response = self._transform_response(response_data, endpoint_config, unified_path)
            
            # Cache the response for GET requests
            if method == 'GET':
                cache_ttl = self._get_cache_ttl(endpoint_config['cache_type'])
                cache.set(cache_key, unified_response, cache_ttl)
            
            return JsonResponse(unified_response)
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'message': str(e),
                'path': path
            }, status=500)

    def _extract_unified_path(self, full_path: str) -> str:
        """Extract the unified path from full request path"""
        # Remove leading/trailing slashes
        clean_path = full_path.strip('/')
        
        # If it starts with v1/, remove it for backward compatibility
        if clean_path.startswith('v1/'):
            clean_path = clean_path[3:]
            
        return clean_path

    def _match_endpoint(self, unified_path: str) -> Optional[Dict]:
        """Match unified path to endpoint configuration"""
        
        # Direct match first
        if unified_path in self.endpoint_mappings:
            return self.endpoint_mappings[unified_path]
        
        # Pattern matching for parameterized endpoints
        for pattern, config in self.endpoint_mappings.items():
            if self._path_matches_pattern(unified_path, pattern):
                return config
        
        return None

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern with parameters"""
        # Convert pattern to regex
        regex_pattern = pattern
        regex_pattern = re.sub(r'\{[^}]+\}', r'[^/]+', regex_pattern)
        regex_pattern = f'^{regex_pattern}$'
        
        return bool(re.match(regex_pattern, path))

    def _route_request(self, endpoint_config: Dict, unified_path: str, request) -> Dict:
        """Route request to appropriate provider"""
        
        provider = endpoint_config['provider']
        
        if provider == 'polygon':
            return self._call_polygon_api(endpoint_config, unified_path, request)
        elif provider == 'fmp':
            return self._call_fmp_api(endpoint_config, unified_path, request)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _call_polygon_api(self, endpoint_config: Dict, unified_path: str, request) -> Dict:
        """Make API call to Polygon.io"""
        
        # Build endpoint URL with path parameters
        endpoint = self._substitute_path_parameters(endpoint_config['endpoint'], unified_path)
        
        url = f"{self.polygon_base_url}{endpoint}"
        
        # Add API key and query parameters
        api_params = dict(request.GET)
        api_params['apikey'] = self.polygon_api_key
        
        # Apply parameter mapping if specified
        if 'params_map' in endpoint_config:
            api_params.update(endpoint_config['params_map'])
        
        # Apply static parameters if specified
        if 'static_params' in endpoint_config:
            api_params.update(endpoint_config['static_params'])
        
        # Clean headers
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in {
                'host', 'connection', 'content-length', 
                'authorization', 'x-request-token'
            }
        }
        
        # Prepare request data
        json_data = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            json_data = getattr(request, 'data', None)
        
        logger.info(f"Calling Polygon API: {url}")
        
        response = self.session.request(
            method=request.method,
            url=url,
            params=api_params,
            headers=headers,
            json=json_data,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        
        try:
            response_json = response.json() if response.content else {}
        except ValueError:
            response_json = {'raw_content': response.text}
        
        return {
            'data': response_json,
            'provider': 'polygon',
            'endpoint': endpoint,
            'status_code': response.status_code
        }

    def _call_fmp_api(self, endpoint_config: Dict, unified_path: str, request) -> Dict:
        """Make API call to FMP Ultimate"""
        
        # Build endpoint URL with path parameters
        endpoint = self._substitute_path_parameters(endpoint_config['endpoint'], unified_path)
        
        url = f"{self.fmp_base_url}{endpoint}"
        
        # Add API key and query parameters
        api_params = dict(request.GET)
        api_params['apikey'] = self.fmp_api_key
        
        # Apply parameter mapping if specified
        if 'params_map' in endpoint_config:
            api_params.update(endpoint_config['params_map'])
        
        # Apply static parameters if specified
        if 'static_params' in endpoint_config:
            api_params.update(endpoint_config['static_params'])
        
        # Clean headers
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in {
                'host', 'connection', 'content-length', 
                'authorization', 'x-request-token'
            }
        }
        
        # Prepare request data
        json_data = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            json_data = getattr(request, 'data', None)
        
        logger.info(f"Calling FMP API: {url}")
        
        response = self.session.request(
            method=request.method,
            url=url,
            params=api_params,
            headers=headers,
            json=json_data,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        
        try:
            response_json = response.json() if response.content else {}
        except ValueError:
            response_json = {'raw_content': response.text}
        
        return {
            'data': response_json,
            'provider': 'fmp',
            'endpoint': endpoint,
            'status_code': response.status_code
        }

    def _substitute_path_parameters(self, endpoint_template: str, unified_path: str) -> str:
        """Substitute path parameters in endpoint template"""
        
        # Extract parameters from unified path
        path_parts = unified_path.split('/')
        
        # Simple parameter substitution
        result = endpoint_template
        
        # Replace common parameters
        if '{symbol}' in result and len(path_parts) >= 2:
            # Find symbol in path (usually second part)
            symbol = path_parts[1] if len(path_parts) > 1 else path_parts[0]
            result = result.replace('{symbol}', symbol)
        
        if '{contract}' in result and len(path_parts) >= 2:
            contract = path_parts[1]
            result = result.replace('{contract}', contract)
        
        if '{cik}' in result and len(path_parts) >= 3:
            cik = path_parts[2]
            result = result.replace('{cik}', cik)
        
        if '{date}' in result and len(path_parts) >= 3:
            date = path_parts[2]
            result = result.replace('{date}', date)
        
        if '{pair}' in result and len(path_parts) >= 2:
            pair = path_parts[1]
            result = result.replace('{pair}', pair)
        
        if '{ticker}' in result and len(path_parts) >= 3:
            ticker = path_parts[2]
            result = result.replace('{ticker}', ticker)
        
        if '{interval}' in result:
            # Default interval or from query params
            interval = '1day'  # default
            result = result.replace('{interval}', interval)
        
        if '{timespan}' in result:
            timespan = 'day'  # default
            result = result.replace('{timespan}', timespan)
        
        if '{multiplier}' in result:
            multiplier = '1'  # default
            result = result.replace('{multiplier}', multiplier)
        
        if '{from}' in result:
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            result = result.replace('{from}', from_date)
        
        if '{to}' in result:
            to_date = datetime.now().strftime('%Y-%m-%d')
            result = result.replace('{to}', to_date)
        
        return result

    def _transform_response(self, response_data: Dict, endpoint_config: Dict, unified_path: str) -> Dict:
        """Transform provider response to unified format"""
        
        provider = endpoint_config['provider']
        data = response_data['data']
        
        # Clean Polygon.io URLs if present
        if provider == 'polygon':
            data = self._clean_polygon_response(data)
        
        # Base unified response
        unified_response = {
            'status': 'success',
            'data': data,
            'metadata': {
                'provider': provider,
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': unified_path,
                'cache_type': endpoint_config['cache_type']
            },
            'request_info': {
                'unified_path': unified_path,
                'provider_endpoint': response_data['endpoint'],
                'routed_to': provider
            }
        }
        
        return unified_response

    def _clean_polygon_response(self, data):
        """Clean Polygon.io specific response data (legacy from PolygonProxyView)"""
        if not isinstance(data, dict):
            return data

        for field in ["status", "request_id", "queryCount"]:
            data.pop(field, None)

        for field in ["next_url", "previous_url", "next", "previous"]:
            if (
                field in data
                and isinstance(data[field], str)
                and "polygon.io" in data[field]
            ):
                url = data[field].replace("api.polygon.io", self.proxy_domain)
                url = re.sub(r"[?&]apikey=[^&]*&?", "", url, flags=re.IGNORECASE)
                url = re.sub(r"/v[1-3]/", "/v1/", url)
                url = re.sub(r"[&?]+$", "", url)
                if not url.startswith("https://"):
                    url = (
                        f"https://{url}"
                        if not url.startswith("http")
                        else url.replace("http://", "https://")
                    )
                data[field] = url

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self._clean_polygon_response(value)
            elif isinstance(value, list):
                data[key] = [
                    self._clean_polygon_response(item) if isinstance(item, dict) else item
                    for item in value
                ]

        return data

    def _check_rate_limit(self, provider: str) -> bool:
        """Check rate limits for provider"""
        
        cache_key = f"rate_limit:{provider}:{datetime.now().strftime('%Y%m%d%H%M')}"
        current_count = cache.get(cache_key, 0)
        
        limit = self.rate_limits[provider]['calls']
        
        if current_count >= limit:
            return False
        
        cache.set(cache_key, current_count + 1, 60)
        return True

    def _generate_cache_key(self, unified_path: str, params: Dict) -> str:
        """Generate cache key for request"""
        
        sorted_params = sorted(params.items())
        params_str = urlencode(sorted_params)
        
        return f"unified_api:{unified_path}:{hash(params_str)}"

    def _get_cache_ttl(self, cache_type: str) -> int:
        """Get cache TTL based on data type"""
        return self.cache_ttl.get(cache_type, self.cache_ttl['daily'])


# Keep the legacy PolygonProxyView for backward compatibility (alias)
PolygonProxyView = UnifiedFinancialAPIView
