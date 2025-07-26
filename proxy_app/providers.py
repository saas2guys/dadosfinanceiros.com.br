"""
Simple provider classes for Polygon.io and FMP Ultimate
"""
import time
from typing import Any, Dict, Optional

import requests

from .config import ProviderError, RateLimitError


class BaseProvider:
    """Base provider class with common functionality"""

    def __init__(self, api_key: str, base_url: str, rate_limit: int = 1000):
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.request_count = 0
        self.session = requests.Session()

    def _check_rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time < 60:  # Within 1 minute
            if self.request_count >= self.rate_limit:
                raise RateLimitError(f"Rate limit exceeded: {self.rate_limit} requests per minute")
        else:
            self.request_count = 0
            self.last_request_time = current_time

        self.request_count += 1

    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to provider API"""
        self._check_rate_limit()

        url = f"{self.base_url}{endpoint}"

        # Add API key to params
        if params is None:
            params = {}
        params['apikey'] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            elif response.status_code == 401:
                raise ProviderError(self.__class__.__name__, "Invalid API key", response.status_code)
            elif response.status_code == 404:
                raise ProviderError(self.__class__.__name__, "Endpoint not found", response.status_code)
            else:
                raise ProviderError(self.__class__.__name__, f"HTTP {response.status_code}: {e}", response.status_code)

        except requests.exceptions.RequestException as e:
            raise ProviderError(self.__class__.__name__, f"Request failed: {e}")


class PolygonProvider(BaseProvider):
    """Polygon.io provider for US market data, options, futures, and tick data"""

    def __init__(self, api_key: str):
        super().__init__(api_key, 'https://api.polygon.io', rate_limit=1000)

    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Override to handle Polygon.io specific API key format"""
        self._check_rate_limit()

        url = f"{self.base_url}{endpoint}"

        # Polygon.io uses apikey parameter
        if params is None:
            params = {}
        params['apikey'] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise RateLimitError(f"Polygon.io rate limit exceeded: {e}")
            elif response.status_code == 401:
                raise ProviderError("Polygon", "Invalid API key", response.status_code)
            elif response.status_code == 404:
                raise ProviderError("Polygon", "Endpoint not found", response.status_code)
            else:
                raise ProviderError("Polygon", f"HTTP {response.status_code}: {e}", response.status_code)

        except requests.exceptions.RequestException as e:
            raise ProviderError("Polygon", f"Request failed: {e}")


class FMPProvider(BaseProvider):
    """Financial Modeling Prep provider for global markets, fundamentals, and news"""

    def __init__(self, api_key: str):
        super().__init__(api_key, 'https://financialmodelingprep.com/api', rate_limit=3000)

    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Override to handle FMP specific API key format"""
        self._check_rate_limit()

        url = f"{self.base_url}{endpoint}"

        # FMP uses apikey parameter
        if params is None:
            params = {}
        params['apikey'] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise RateLimitError(f"FMP rate limit exceeded: {e}")
            elif response.status_code == 401:
                raise ProviderError("FMP", "Invalid API key", response.status_code)
            elif response.status_code == 404:
                raise ProviderError("FMP", "Endpoint not found", response.status_code)
            else:
                raise ProviderError("FMP", f"HTTP {response.status_code}: {e}", response.status_code)

        except requests.exceptions.RequestException as e:
            raise ProviderError("FMP", f"Request failed: {e}")


# Provider factory
def get_provider(provider_name: str, api_key: str) -> BaseProvider:
    """Factory function to get provider instance"""
    providers = {'polygon': PolygonProvider, 'fmp': FMPProvider}

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}")

    return providers[provider_name](api_key)
