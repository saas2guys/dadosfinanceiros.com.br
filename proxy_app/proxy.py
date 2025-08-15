"""
Main proxy logic for routing requests, caching, and response transformation
"""
import logging
import re
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

from django.conf import settings

from .config import (
    CACHE_TTL,
    ENDPOINT_ROUTES,
    FMP_API_KEY,
    POLYGON_API_KEY,
    EndpointNotFoundError,
    FinancialAPIError,
    ProviderError,
)
from .providers import get_provider

# Set up logging
logger = logging.getLogger(__name__)


class FinancialDataProxy:
    """Main proxy class that handles all request routing and processing"""

    def __init__(self, providers: Optional[dict] = None):
        if providers:
            self.providers = providers
        else:
            self.providers = {'polygon': get_provider('polygon', POLYGON_API_KEY), 'fmp': get_provider('fmp', FMP_API_KEY)}


    def process_request(self, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main method to process incoming requests

        Args:
            path: API endpoint path (e.g., "quotes/AAPL")
            params: Query parameters

        Returns:
            JSON response data
        """
        try:
            # Use LRU-cached computation of provider call and transformation
            before_hits = self._fetch_and_transform_cached.cache_info().hits
            data, provider_name = self._fetch_and_transform_cached(
                path,
                self._params_to_key(params),
            )
            after_hits = self._fetch_and_transform_cached.cache_info().hits
            source = "cache" if after_hits > before_hits else "live"
            return self._add_metadata(data, source, provider_name)
        except FinancialAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing {path}: {e}")
            raise FinancialAPIError(f"Internal error: {e}")

    def _find_route(self, path: str) -> Optional[Dict[str, Any]]:
        """Find matching route configuration for the given path"""
        for route_pattern, config in ENDPOINT_ROUTES.items():
            # Convert route pattern to regex
            regex_pattern = route_pattern.replace('{', '(?P<').replace('}', '>[^/]+)')
            regex_pattern = f"^{regex_pattern}$"

            if re.match(regex_pattern, path):
                return config

        return None

    def _params_to_key(self, params: Optional[Dict[str, Any]]) -> Tuple[Tuple[str, str], ...]:
        """Convert params dict to a hashable, deterministic tuple for caching."""
        if not params:
            return tuple()
        return tuple(sorted((str(k), str(v)) for k, v in params.items()))

    # Use module import time setting for cache size
    _LRU_MAXSIZE = getattr(settings, "PROXY_LRU_CACHE_SIZE", 1024)

    @lru_cache(maxsize=_LRU_MAXSIZE)
    def _fetch_and_transform_cached(
        self, path: str, params_key: Tuple[Tuple[str, str], ...]
    ) -> Tuple[Dict[str, Any], str]:
        """
        LRU-cached core pipeline: route lookup, transform request, provider call, transform response.
        Returns a tuple of (transformed_data, provider_name).
        The params are supplied as a hashable tuple to make the cache key stable.
        """
        # 1. Find matching route
        route_config = self._find_route(path)
        if not route_config:
            raise EndpointNotFoundError(f"Endpoint not found: {path}")

        # 2. Transform path and params for provider
        params_dict = dict(params_key)
        provider_endpoint, provider_params = self._transform_request(path, params_dict, route_config)

        # 3. Make request to provider
        provider = self.providers[route_config["provider"]]
        response_data = provider.make_request(provider_endpoint, provider_params)

        # 4. Transform response if needed
        transformed_data = self._transform_response(response_data, route_config)

        return transformed_data, route_config["provider"]

    def _transform_request(self, path: str, params: Dict[str, Any], route_config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Transform the request path and parameters for the target provider"""
        provider_endpoint = route_config["endpoint"]
        provider_params = params.copy() if params else {}

        # Extract path parameters (e.g., {symbol} from path)
        route_pattern = None
        for pattern, config in ENDPOINT_ROUTES.items():
            if config == route_config:
                route_pattern = pattern
                break

        if route_pattern:
            # Convert route pattern to regex with named groups
            regex_pattern = route_pattern.replace('{', '(?P<').replace('}', '>[^/]+)')
            regex_pattern = f"^{regex_pattern}$"

            match = re.match(regex_pattern, path)
            if match:
                path_params = match.groupdict()

                # Replace placeholders in provider endpoint
                for param_name, param_value in path_params.items():
                    placeholder = f"{{{param_name}}}"
                    provider_endpoint = provider_endpoint.replace(placeholder, param_value)

        # Add any additional parameters from route config
        if "params" in route_config:
            for param_name, param_value in route_config["params"].items():
                # Replace placeholders in parameter values
                if isinstance(param_value, str) and "{" in param_value:
                    route_pattern = None
                    for pattern, config in ENDPOINT_ROUTES.items():
                        if config == route_config:
                            route_pattern = pattern
                            break

                    if route_pattern:
                        regex_pattern = route_pattern.replace('{', '(?P<').replace('}', '>[^/]+)')
                        regex_pattern = f"^{regex_pattern}$"
                        match = re.match(regex_pattern, path)
                        if match:
                            path_params = match.groupdict()
                            for path_param_name, path_param_value in path_params.items():
                                placeholder = f"{{{path_param_name}}}"
                                param_value = param_value.replace(placeholder, path_param_value)

                provider_params[param_name] = param_value

        return provider_endpoint, provider_params

    def _transform_response(self, response_data: Dict[str, Any], route_config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform provider response to unified format and replace URLs with financialdata.online"""
        transformed_data = response_data.copy()

        transformed_data = self._replace_urls_in_response(transformed_data)

        return transformed_data

    def _replace_urls_in_response(self, data: Any) -> Any:
        """Recursively replace any URLs in the response data with financialdata.online URLs"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key.lower() in ['url', 'link', 'href', 'endpoint', 'next_url', 'previous_url']:
                    result[key] = self._convert_to_financialdata_url(value)
                else:
                    result[key] = self._replace_urls_in_response(value)
            return result
        elif isinstance(data, list):
            return [self._replace_urls_in_response(item) for item in data]
        elif isinstance(data, str):
            if self._is_provider_url(data):
                return self._convert_to_financialdata_url(data)
            return data
        else:
            return data

    def _is_provider_url(self, text: str) -> bool:
        """Check if a string looks like a provider URL that should be replaced"""
        provider_domains = [
            'polygon.io',
            'financialmodelingprep.com',
            'api.polygon.io',
            'fmp-cloud-io',
        ]

        return any(domain in text.lower() for domain in provider_domains)

    def _convert_to_financialdata_url(self, original_url: str) -> str:
        """Convert a provider URL to a financialdata.online URL"""
        if not isinstance(original_url, str) or not original_url.strip():
            return original_url

        if 'financialdata.online' in original_url.lower():
            return original_url

        if not self._is_provider_url(original_url):
            return original_url

        import urllib.parse

        try:
            parsed = urllib.parse.urlparse(original_url)
            path = parsed.path
            query = parsed.query

            if path.startswith('/v1/') or path.startswith('/v2/') or path.startswith('/v3/'):
                path = path[4:]

            new_url = f"{settings.FINANCIALDATA_BASE_URL}/api/v1{path}"

            if query:
                new_url += f"?{query}"

            return new_url

        except Exception as e:
            logger.warning(f"Failed to convert URL {original_url}: {e}")
            return original_url

    def _add_metadata(self, data: Dict[str, Any], source: str, provider: str) -> Dict[str, Any]:
        """Add metadata to response"""
        if isinstance(data, dict):
            data["_metadata"] = {"source": source, "provider": provider, "timestamp": self._get_current_timestamp()}  # "cache" or "live"

        return data

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all providers"""
        health_status = {"status": "healthy", "providers": {}, "timestamp": self._get_current_timestamp()}

        for provider_name, provider in self.providers.items():
            try:
                # Test with a simple endpoint
                if provider_name == "polygon":
                    test_endpoint = "/v1/marketstatus/now"
                else:  # fmp
                    test_endpoint = "/v3/quote/AAPL"

                provider.make_request(test_endpoint, {"limit": 1})
                health_status["providers"][provider_name] = {"status": "healthy", "last_check": self._get_current_timestamp()}
            except Exception as e:
                health_status["providers"][provider_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": self._get_current_timestamp(),
                }
                health_status["status"] = "degraded"

        return health_status

    def get_endpoint_list(self) -> Dict[str, Any]:
        """Get list of all available endpoints"""
        endpoints = []

        for route_pattern, config in ENDPOINT_ROUTES.items():
            endpoints.append(
                {
                    "endpoint": f"/api/v1/{route_pattern}",
                    "provider": config["provider"],
                    "cache_ttl": CACHE_TTL.get(config.get("cache"), 3600),
                    "description": self._get_endpoint_description(route_pattern),
                }
            )

        return {
            "total_endpoints": len(endpoints),
            "endpoints": sorted(endpoints, key=lambda x: x["endpoint"]),
            "providers": list(self.providers.keys()),
        }

    def _get_endpoint_description(self, route_pattern: str) -> str:
        """Get human-readable description for endpoint"""
        descriptions = {
            "quotes/{symbol}": "Get real-time quote for a symbol",
            "historical/{symbol}": "Get historical price data",
            "options/chain/{symbol}": "Get options chain with Greeks",
            "fundamentals/{symbol}/ratios": "Get financial ratios",
            "news/{symbol}": "Get news for a symbol",
            # Add more descriptions as needed
        }

        return descriptions.get(route_pattern, "Financial data endpoint")


# Global proxy instance
proxy = FinancialDataProxy()
