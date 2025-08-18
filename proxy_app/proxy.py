"""
Main proxy logic for routing requests, caching, and response transformation
"""
import logging
import re
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

from django.conf import settings

from .config import (
    ENDPOINT_ROUTES,
    FMP_API_KEY,
    POLYGON_API_KEY,
    EndpointNotFoundError,
    FinancialAPIError,
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
            # Get data from cache or provider
            data, provider_name, from_cache = self._get_data(path, params or {})

            # Add metadata and return
            return self._add_metadata(data, provider_name, from_cache)

        except FinancialAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing {path}: {e}")
            raise FinancialAPIError(f"Internal error: {e}")

    @lru_cache(maxsize=1024)
    def _get_data(self, path: str, params_tuple: Tuple[Tuple[str, str], ...]) -> Tuple[Dict[str, Any], str, bool]:
        """Get data from provider (cached)"""
        # Check if we got cache hit
        cache_info_before = self._get_data.cache_info()

        # Find route configuration
        route_config = self._find_route(path)
        if not route_config:
            raise EndpointNotFoundError(f"Endpoint not found: {path}")

        # Convert params back to dict
        params = dict(params_tuple)

        # Transform request for provider
        provider_endpoint, provider_params = self._transform_request(path, params, route_config)

        # Call provider
        provider = self.providers[route_config["provider"]]
        response_data = provider.make_request(provider_endpoint, provider_params)

        # Transform response
        transformed_data = self._transform_response(response_data)

        # Check if this was a cache hit
        cache_info_after = self._get_data.cache_info()
        from_cache = cache_info_after.hits > cache_info_before.hits

        return transformed_data, route_config["provider"], from_cache

    def process_request(self, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process request - public interface"""
        # Convert params to hashable tuple for caching
        params_tuple = self._dict_to_tuple(params or {})

        try:
            data, provider_name, from_cache = self._get_data(path, params_tuple)
            return self._add_metadata(data, provider_name, from_cache)
        except FinancialAPIError:
            raise
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            raise FinancialAPIError(f"Internal error: {e}")

    def _find_route(self, path: str) -> Optional[Dict[str, Any]]:
        """Find matching route for path"""
        for pattern, config in ENDPOINT_ROUTES.items():
            if self._path_matches_pattern(path, pattern):
                return config
        return None

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches route pattern"""
        regex_pattern = pattern.replace('{', '(?P<').replace('}', '>[^/]+)')
        return bool(re.match(f"^{regex_pattern}$", path))

    def _transform_request(self, path: str, params: Dict[str, Any], route_config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Transform the request path and parameters for the target provider"""
        provider_endpoint = route_config["endpoint"]
        provider_params = params.copy()

        # Extract path parameters (e.g., {symbol} from quotes/{symbol})
        path_params = self._extract_path_params(path, route_config)

        # Replace placeholders in endpoint
        for param_name, param_value in path_params.items():
            provider_endpoint = provider_endpoint.replace(f"{{{param_name}}}", param_value)

        # Add configured parameters
        if "params" in route_config:
            for param_name, param_value in route_config["params"].items():
                # Replace path params in configured values
                for path_param_name, path_param_value in path_params.items():
                    param_value = str(param_value).replace(f"{{{path_param_name}}}", path_param_value)
                provider_params[param_name] = param_value

        return provider_endpoint, provider_params

    def _extract_path_params(self, path: str, route_config: Dict[str, Any]) -> Dict[str, str]:
        """Extract parameters from path using route pattern"""
        # Find the route pattern for this config
        route_pattern = None
        for pattern, config in ENDPOINT_ROUTES.items():
            if config == route_config:
                route_pattern = pattern
                break

        if not route_pattern:
            return {}

        # Extract parameters
        regex_pattern = route_pattern.replace('{', '(?P<').replace('}', '>[^/]+)')
        match = re.match(f"^{regex_pattern}$", path)

        return match.groupdict() if match else {}

    def _transform_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform provider response to replace URLs"""
        return self._replace_provider_urls(response_data)

    def _replace_provider_urls(self, data: Any) -> Any:
        """Recursively replace provider URLs with financialdata.online URLs"""
        if isinstance(data, dict):
            return {
                key: self._convert_url(value) if self._is_url_field(key) else self._replace_provider_urls(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._replace_provider_urls(item) for item in data]
        elif isinstance(data, str) and self._is_provider_url(data):
            return self._convert_url(data)
        return data

    def _is_url_field(self, field_name: str) -> bool:
        """Check if field contains URLs"""
        url_fields = ['url', 'link', 'href', 'endpoint', 'next_url', 'previous_url']
        return field_name.lower() in url_fields

    def _is_provider_url(self, text: str) -> bool:
        """Check if string is a provider URL"""
        provider_domains = ['polygon.io', 'financialmodelingprep.com', 'api.polygon.io', 'fmp-cloud-io']
        return any(domain in text.lower() for domain in provider_domains)

    def _convert_url(self, url: str) -> str:
        """Convert provider URL to financialdata.online URL"""
        if not isinstance(url, str) or 'financialdata.online' in url.lower():
            return url

        if not self._is_provider_url(url):
            return url

        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)

            # Remove version prefix from path
            path = parsed.path
            if path.startswith(('/v1/', '/v2/', '/v3/')):
                path = path[4:]

            # Build new URL
            new_url = f"{settings.FINANCIALDATA_BASE_URL}/api/v1{path}"
            if parsed.query:
                new_url += f"?{parsed.query}"

            return new_url
        except Exception as e:
            logger.warning(f"Failed to convert URL {url}: {e}")
            return url

    def _add_metadata(self, data: Dict[str, Any], provider: str, from_cache: bool) -> Dict[str, Any]:
        """Add metadata to response"""
        if isinstance(data, dict):
            data["_metadata"] = {
                "source": "cache" if from_cache else "live",
                "provider": provider,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        return data

    def _dict_to_tuple(self, params: Dict[str, Any]) -> Tuple[Tuple[str, str], ...]:
        """Convert dict to sorted tuple for caching"""
        return tuple(sorted((str(k), str(v)) for k, v in params.items()))

    # Health and documentation methods
    def get_health_status(self) -> Dict[str, Any]:
        """Get provider health status"""
        status = {"status": "healthy", "providers": {}, "timestamp": datetime.utcnow().isoformat() + "Z"}

        for name, provider in self.providers.items():
            try:
                # Simple health check
                test_endpoint = "/v1/marketstatus/now" if name == "polygon" else "/v3/quote/AAPL"
                provider.make_request(test_endpoint, {"limit": 1})
                status["providers"][name] = {"status": "healthy"}
            except Exception as e:
                status["providers"][name] = {"status": "unhealthy", "error": str(e)}
                status["status"] = "degraded"

        return status

    def get_endpoint_list(self) -> Dict[str, Any]:
        """Get available endpoints"""
        endpoints = [
            {
                "endpoint": f"/api/v1/{pattern}",
                "provider": config["provider"],
                "description": self._get_description(pattern)
            }
            for pattern, config in ENDPOINT_ROUTES.items()
        ]

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
