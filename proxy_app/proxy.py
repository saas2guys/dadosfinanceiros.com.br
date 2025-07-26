"""
Main proxy logic for routing requests, caching, and response transformation
"""
import json
import logging
import re
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.core.cache import cache

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

    def __init__(self):
        # Initialize providers
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
            # 1. Find matching route
            route_config = self._find_route(path)
            if not route_config:
                raise EndpointNotFoundError(f"Endpoint not found: {path}")

            # 2. Check cache first
            cache_key = self._generate_cache_key(path, params)
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for {path}")
                return self._add_metadata(cached_data, "cache", route_config["provider"])

            # 3. Transform path and params for provider
            provider_endpoint, provider_params = self._transform_request(path, params, route_config)

            # 4. Make request to provider
            provider = self.providers[route_config["provider"]]
            response_data = provider.make_request(provider_endpoint, provider_params)

            # 5. Transform response if needed
            transformed_data = self._transform_response(response_data, route_config)

            # 6. Cache the result
            cache_ttl = CACHE_TTL.get(route_config["cache"], 3600)
            cache.set(cache_key, transformed_data, cache_ttl)

            # 7. Add metadata and return
            return self._add_metadata(transformed_data, "live", route_config["provider"])

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

    def _generate_cache_key(self, path: str, params: Dict[str, Any] = None) -> str:
        """Generate cache key for the request"""
        key_parts = [path]

        if params:
            # Sort params for consistent cache keys
            sorted_params = sorted(params.items())
            params_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            key_parts.append(params_str)

        return f"financial_api:{'|'.join(key_parts)}"

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
        """Transform provider response to unified format"""
        # For now, return response as-is
        # In the future, you could add response normalization here
        return response_data

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
                    "cache_ttl": CACHE_TTL.get(config["cache"], 3600),
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
