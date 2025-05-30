import logging
import re
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings
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


@permission_classes([AllowAny])
def api_documentation(request):
    return render(request, "api/docs.html")


class PolygonProxyView(APIView):
    renderer_classes = [JSONRenderer]
    authentication_classes = [JWTAuthentication, RequestTokenAuthentication]
    permission_classes = [IsAuthenticated, DailyLimitPermission]

    V2_ENDPOINTS = [
        "aggs",
        "snapshot/locale/us/markets",
        "last/trade",
        "last/nbbo",
        "fed/vx/treasury-yields",
        "benzinga/v1/ratings",
        "grouped/locale/us/market",
    ]

    V1_ENDPOINTS = [
        "conversion",
        "open-close",
        "related-companies",
        "meta/symbols",
        "meta/exchanges",
        "historic/trades",
        "historic/quotes",
        "last/currencies",
    ]

    EXCLUDED_HEADERS = {
        "host",
        "connection",
        "content-length",
        "authorization",
        "x-request-token",
    }

    PAGINATION_FIELDS = [
        "next_url",
        "previous_url",
        "next",
        "previous",
        "first_url",
        "last_url",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_configuration()
        self._setup_local_environment()

    def _setup_configuration(self):
        self.base_url = settings.POLYGON_BASE_URL
        self.api_key = settings.POLYGON_API_KEY
        self.timeout = getattr(settings, "PROXY_TIMEOUT", 30)
        self.proxy_domain = getattr(
            settings, "PROXY_DOMAIN", "api.dadosfinanceiros.com.br"
        )
        self.session = requests.Session()

    def _setup_local_environment(self):
        if settings.ENV == "local":
            logger.info("Using no auth and no permissions for local environment!")
            self.authentication_classes = []
            self.permission_classes = [AllowAny]

    def get_market_config(self, market):
        """Return configuration for specified market"""
        configs = {
            "us": {
                "base_url": getattr(
                    settings, "POLYGON_BASE_URL", "https://api.polygon.io"
                ),
                "api_key_header": "apikey",
                "api_key": getattr(settings, "POLYGON_API_KEY"),
                "ticker_format": self.format_us_ticker,
                "data_processor": self.process_polygon_response,
            },
            "br": {
                "base_url": getattr(
                    settings, "B3_BASE_URL", "https://api-marketdata.b3.com.br"
                ),
                "fallback_urls": [
                    getattr(settings, "CEDRO_BASE_URL", "https://api.cedrotech.com"),
                    getattr(
                        settings,
                        "B3_HISTORICAL_URL",
                        "https://cvscarlos.github.io/b3-api-dados-historicos/api/v1",
                    ),
                ],
                "api_key_header": "KeyId",
                "api_key": getattr(settings, "B3_API_KEY", None),
                "fallback_keys": {
                    "cedro": getattr(settings, "CEDRO_API_KEY", None),
                },
                "ticker_format": self.format_br_ticker,
                "data_processor": self.process_b3_response,
            },
        }
        return configs.get(market)

    def format_br_ticker(self, ticker):
        """Convert ticker to Brazilian format"""
        ticker = ticker.upper()

        # US ADR/BDR mappings
        us_to_br_mapping = {
            "AAPL": "AAPL34",
            "MSFT": "MSFT34",
            "GOOGL": "GOGL34",
            "TSLA": "TSLA34",
            "AMZN": "AMZO34",
            "META": "M1TA34",
            "NVDA": "NVDC34",
            "NFLX": "NFLX34",
            "CRM": "SAXO34",
            "PYPL": "PYPL34",
        }

        # Popular Brazilian stocks (pass through)
        br_stocks = {
            "PETR4",
            "PETR3",
            "VALE3",
            "ITUB4",
            "BBDC4",
            "ABEV3",
            "SUZB3",
            "RENT3",
            "LREN3",
            "MGLU3",
            "WEGE3",
            "JBSS3",
            "BRFS3",
            "CCRO3",
            "VIVT3",
        }

        if ticker in us_to_br_mapping:
            return us_to_br_mapping[ticker]
        elif ticker in br_stocks:
            return ticker
        else:
            # Default: assume it's already in BR format
            return ticker

    def format_us_ticker(self, ticker):
        """Format ticker for US market (existing logic)"""
        return ticker.upper()

    def process_polygon_response(self, response_data, endpoint_type, original_path):
        """Process Polygon.io response (existing logic)"""
        return response_data

    def process_b3_response(self, response_data, endpoint_type, original_path):
        """Convert B3 response to Polygon.io format"""

        if endpoint_type == "aggregates":
            return self.process_b3_aggregates(response_data)
        elif endpoint_type == "last_trade":
            return self.process_b3_last_trade(response_data)
        elif endpoint_type == "last_quote":
            return self.process_b3_last_quote(response_data)
        elif endpoint_type == "tickers_list":
            return self.process_b3_tickers(response_data)
        elif endpoint_type == "market_status":
            return self.process_b3_market_status(response_data)
        else:
            return response_data

    def process_b3_aggregates(self, data):
        """Convert B3 historical data to Polygon aggregates format"""
        results = []

        # Handle different B3 data sources
        if "data" in data:  # B3 historical API format
            for date_str, values in data.get("data", {}).items():
                bar = {
                    "c": values.get("close"),
                    "h": values.get("high"),
                    "l": values.get("low"),
                    "o": values.get("open"),
                    "t": self.convert_br_date_to_timestamp(date_str),
                    "v": values.get("volume", 0),
                    "vw": values.get("vwap", values.get("close")),
                    "n": values.get("transactions", 0),
                }
                results.append(bar)

        elif "quotes" in data:  # Cedro API format
            for quote in data.get("quotes", []):
                bar = {
                    "c": quote.get("close"),
                    "h": quote.get("high"),
                    "l": quote.get("low"),
                    "o": quote.get("open"),
                    "t": quote.get("timestamp"),
                    "v": quote.get("volume", 0),
                    "vw": quote.get("vwap", quote.get("close")),
                    "n": quote.get("trades", 0),
                }
                results.append(bar)

        return {"results": results, "resultsCount": len(results), "adjusted": True}

    def process_b3_last_trade(self, data):
        """Convert B3 trade data to Polygon format"""
        return {
            "results": {
                "conditions": [1],  # Regular trade
                "exchange": 147,  # B3 exchange ID
                "price": data.get("last_price") or data.get("price"),
                "size": data.get("last_volume") or data.get("volume", 100),
                "timestamp": int(datetime.now().timestamp() * 1000000000),
                "timeframe": "REAL-TIME",
            }
        }

    def process_b3_last_quote(self, data):
        """Convert B3 quote data to Polygon NBBO format"""
        return {
            "results": {
                "ask": data.get("ask_price") or data.get("ask"),
                "ask_exchange": 147,
                "ask_size": data.get("ask_size") or data.get("ask_volume", 100),
                "bid": data.get("bid_price") or data.get("bid"),
                "bid_exchange": 147,
                "bid_size": data.get("bid_size") or data.get("bid_volume", 100),
                "exchange": 147,
                "timestamp": int(datetime.now().timestamp() * 1000000000),
            }
        }

    def process_b3_tickers(self, data):
        """Convert B3 ticker list to Polygon format"""
        results = []

        if "data" in data:  # B3 format
            for ticker, info in data.get("data", {}).items():
                result = {
                    "ticker": ticker,
                    "name": info.get("nomeCurto", ticker),
                    "market": "stocks",
                    "locale": "br",
                    "currency_name": "BRL",
                    "active": True,
                    "cik": None,
                    "composite_figi": None,
                    "share_class_figi": None,
                    "last_updated_utc": datetime.now().isoformat(),
                }
                results.append(result)

        return {"results": results, "count": len(results)}

    def process_b3_market_status(self, data):
        """Process B3 market status"""
        return {"results": self.get_br_market_status()}

    def make_b3_request(self, endpoint_type, path_parts, query_params, market_config):
        """Make request to B3 APIs with fallback logic"""

        # Try primary B3 API first
        try:
            response = self.try_b3_official_api(
                endpoint_type, path_parts, query_params, market_config
            )
            if response:
                return response
        except Exception as e:
            logger.warning(f"B3 Official API failed: {e}")

        # Try Cedro API as fallback
        try:
            response = self.try_cedro_api(
                endpoint_type, path_parts, query_params, market_config
            )
            if response:
                return response
        except Exception as e:
            logger.warning(f"Cedro API failed: {e}")

        # Try free B3 historical data as last resort
        try:
            response = self.try_b3_historical_api(
                endpoint_type, path_parts, query_params, market_config
            )
            if response:
                return response
        except Exception as e:
            logger.warning(f"B3 Historical API failed: {e}")

        return None

    def try_b3_official_api(
        self, endpoint_type, path_parts, query_params, market_config
    ):
        """Try B3 official market data API"""
        base_url = market_config["base_url"]

        if endpoint_type == "aggregates":
            # Construct B3 aggregates URL
            ticker = self.format_br_ticker(path_parts[3])
            from_date = path_parts[7]
            to_date = path_parts[8]

            url = f"{base_url}/api/historical/v1/series"
            params = {"symbol": ticker, "startDate": from_date, "endDate": to_date}

            headers = {market_config["api_key_header"]: market_config["api_key"]}
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()

        return None

    def try_cedro_api(self, endpoint_type, path_parts, query_params, market_config):
        """Try Cedro Technologies API"""
        cedro_key = market_config["fallback_keys"].get("cedro")
        if not cedro_key:
            return None

        base_url = market_config["fallback_urls"][0]
        ticker = self.format_br_ticker(path_parts[3])

        headers = {"Authorization": f"Bearer {cedro_key}"}

        if endpoint_type == "last_trade" or endpoint_type == "last_quote":
            url = f"{base_url}/sinacor/v1/quotes/{ticker}"
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                return response.json()

        elif endpoint_type == "aggregates":
            url = f"{base_url}/sinacor/v1/quotes/{ticker}/history"
            params = {
                "from": path_parts[7],
                "to": path_parts[8],
                "interval": f"{path_parts[5]}{path_parts[6][0]}",
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()

        return None

    def try_b3_historical_api(
        self, endpoint_type, path_parts, query_params, market_config
    ):
        """Try free B3 historical data API"""
        if endpoint_type not in ["aggregates", "tickers_list"]:
            return None

        base_url = market_config["fallback_urls"][1]

        if endpoint_type == "tickers_list":
            url = f"{base_url}/tickers-cash-market.json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()

        return None

    def convert_br_date_to_timestamp(self, date_str):
        """Convert Brazilian date format to timestamp"""
        try:
            # Handle YYYYMMDD format
            if len(date_str) == 8:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
            else:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            return int(date_obj.timestamp() * 1000)
        except:
            return int(datetime.now().timestamp() * 1000)

    def generate_request_id(self):
        """Generate unique request ID"""
        return f"proxy_{datetime.now().timestamp()}"

    def get_br_market_status(self):
        """Get Brazilian market status"""
        # B3 trading hours: 10:00 AM - 5:30 PM BRT (UTC-3)
        br_tz = timezone(timedelta(hours=-3))
        now = datetime.now(br_tz)

        market_open = now.replace(hour=10, minute=0, second=0, microsecond=0)
        market_close = now.replace(hour=17, minute=30, second=0, microsecond=0)

        is_open = market_open <= now <= market_close and now.weekday() < 5

        return {
            "afterHours": not is_open and now > market_close,
            "market": "open" if is_open else "closed",
            "preMarket": not is_open and now < market_open,
            "serverTime": now.isoformat(),
        }

    def parse_polygon_path(self, path):
        """Parse Polygon.io path to determine endpoint type"""
        path_parts = path.split("/")

        if "aggs" in path:
            endpoint_type = "aggregates"
        elif "last/trade" in path:
            endpoint_type = "last_trade"
        elif "last/nbbo" in path:
            endpoint_type = "last_quote"
        elif "meta/symbols" in path or "grouped" in path:
            endpoint_type = "tickers_list"
        elif "marketstatus" in path:
            endpoint_type = "market_status"
        else:
            endpoint_type = "other"

        return {"type": endpoint_type, "path_parts": path_parts}

    def _get_polygon_version(self, path):
        for endpoint in self.V2_ENDPOINTS:
            if endpoint in path:
                return "v2"

        for endpoint in self.V1_ENDPOINTS:
            if endpoint in path:
                return "v1"

        return "v3"

    def _build_target_url(self, path, market_config=None):
        if market_config:
            # Use market_config for B3 URLs - simplified for now
            return f"{market_config['base_url']}/{path}"

        # Original Polygon.io logic
        clean_path = path.replace("v1/", "")

        # Handle fed and benzinga endpoints with potential additional path components
        if clean_path.startswith(("fed/", "benzinga/")):
            return f"{self.base_url}/{clean_path}"

        # Check if this is a treasury yields endpoint that should use v2
        if "fed/vx/treasury-yields" in clean_path:
            return f"{self.base_url}/v2/{clean_path}"

        version = self._get_polygon_version(clean_path)

        if self._needs_snapshot_prefix(clean_path):
            clean_path = (
                f"snapshot/locale/us/markets/{clean_path.split('snapshot/')[-1]}"
            )

        return f"{self.base_url}/{version}/{clean_path}"

    def _needs_snapshot_prefix(self, path):
        return "snapshot" in path and not path.startswith("snapshot/locale")

    def _clean_headers(self, request_headers):
        return {
            k: v
            for k, v in request_headers.items()
            if k.lower() not in self.EXCLUDED_HEADERS
        }

    def _get_user_info(self, request):
        if hasattr(request, "user") and request.user.is_authenticated:
            return getattr(request.user, "email", str(request.user))
        return "anonymous"

    def _replace_polygon_urls(self, data, request):
        if not isinstance(data, dict):
            return data

        # Process top-level pagination fields
        for field in self.PAGINATION_FIELDS:
            if self._has_polygon_url(data, field):
                data[field] = self._transform_url(data[field])
                logger.debug(f"Replaced {field}: {data[field]}")

        # Process nested objects that might contain pagination URLs
        for key, value in data.items():
            if isinstance(value, dict):
                # Recursively process nested dictionaries
                data[key] = self._replace_polygon_urls(value, request)
            elif isinstance(value, list):
                # Process lists that might contain dictionaries with URLs
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        value[i] = self._replace_polygon_urls(item, request)

        return data

    def _has_polygon_url(self, data, field):
        return (
            field in data
            and isinstance(data[field], str)
            and "polygon.io" in data[field]
        )

    def _transform_url(self, url):
        # Remove API key
        url = re.sub(r"[?&]apikey=[^&]*&?", "", url, flags=re.IGNORECASE)
        url = re.sub(r"[&?]+$", "", url)
        url = re.sub(r"&+", "&", url)

        # Replace domain
        url = url.replace("api.polygon.io", self.proxy_domain)

        # Ensure HTTPS
        url = self._ensure_https(url)

        # Convert Polygon version paths to our legacy format for backward compatibility
        # Transform /v2/path or /v3/path to /v1/path (no market selector for pagination URLs)
        url = re.sub(r"/v[2-3]/", "/v1/", url)

        return url

    def _ensure_https(self, url):
        if url.startswith("http://"):
            return url.replace("http://", "https://")
        elif not url.startswith("https://"):
            return f"https://{url}"
        return url

    def _make_request(self, method, url, params, headers, data=None):
        return self.session.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json=data,
            timeout=self.timeout,
        )

    def _handle_request(self, request, path, market=None):
        try:
            # Validate market parameter if provided
            if market and market not in ["us", "br"]:
                return Response(
                    {
                        "status": "ERROR",
                        "error": f"Invalid market '{market}'. Use 'us' or 'br'",
                        "request_id": self.generate_request_id(),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Default to US market for backward compatibility
            if not market:
                market = "us"

            # Get market configuration
            market_config = self.get_market_config(market)
            if not market_config:
                return Response(
                    {
                        "status": "ERROR",
                        "error": f"Market '{market}' not configured",
                        "request_id": self.generate_request_id(),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Parse endpoint
            parsed = self.parse_polygon_path(path)
            endpoint_type = parsed["type"]
            path_parts = parsed["path_parts"]
            query_params = request.GET
            user_info = self._get_user_info(request)

            logger.info(
                f"Forwarding {request.method} request for {market} market to: {path} by user: {user_info}"
            )

            # Route to appropriate market handler
            if market == "us":
                # Use existing Polygon.io logic
                target_url = self._build_target_url(path)
                params = {**request.GET.dict(), "apiKey": self.api_key}
                headers = self._clean_headers(request.headers)

                json_data = (
                    request.data if request.method in ["POST", "PUT", "PATCH"] else None
                )
                response = self._make_request(
                    request.method, target_url, params, headers, json_data
                )

                logger.info(f"US market response status code: {response.status_code}")
                return self._process_response(response, request)

            else:  # market == 'br'
                # Use new B3 logic
                response_data = self.make_b3_request(
                    endpoint_type, path_parts, query_params, market_config
                )
                if response_data is None:
                    return Response(
                        {
                            "status": "ERROR",
                            "error": "No data available from any B3 source",
                            "request_id": self.generate_request_id(),
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                processed_data = market_config["data_processor"](
                    response_data, endpoint_type, path
                )
                return Response(data=processed_data, status=status.HTTP_200_OK)

        except requests.Timeout:
            return self._error_response(
                "Gateway Timeout",
                "The request timed out",
                status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except requests.RequestException as e:
            return self._error_response(
                "Bad Gateway", str(e), status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            logger.error(f"Proxy error for {market} market: {str(e)}")
            return self._error_response(
                "Internal Server Error", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _process_response(self, response, request):
        try:
            data = response.json() if response.content else {}

            if data:
                data = self._replace_polygon_urls(data, request)
                # Remove Polygon.io specific fields that shouldn't be exposed to users
                data.pop("status", None)
                data.pop("request_id", None)
                data.pop("queryCount", None)

            return Response(data=data, status=response.status_code)

        except ValueError:
            if response.status_code == 404:
                return self._error_response(
                    "Not Found",
                    "The requested resource was not found",
                    status.HTTP_404_NOT_FOUND,
                )
            return Response(
                data={"error": "Invalid JSON response", "content": response.text},
                status=response.status_code,
            )

    def _error_response(self, error, message, status_code):
        logger.error(f"{error}: {message}")
        return Response({"error": error, "message": message}, status=status_code)

    def _increment_user_request_count(self, request, response):
        """Increment user's daily request count for successful responses"""
        if (
            hasattr(request, "user")
            and request.user.is_authenticated
            and 200 <= response.status_code < 400
        ):  # Success status codes
            request.user.increment_request_count()

    def get(self, request, path, market=None):
        response = self._handle_request(request, path, market)
        self._increment_user_request_count(request, response)
        return response

    def post(self, request, path, market=None):
        response = self._handle_request(request, path, market)
        self._increment_user_request_count(request, response)
        return response

    def put(self, request, path, market=None):
        response = self._handle_request(request, path, market)
        self._increment_user_request_count(request, response)
        return response

    def delete(self, request, path, market=None):
        response = self._handle_request(request, path, market)
        self._increment_user_request_count(request, response)
        return response
