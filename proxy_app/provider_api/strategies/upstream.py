from typing import Any, Iterable, Tuple

import httpx

from ..config import ProviderConfig


class HttpxClient:
    """HTTPX-based upstream client.

    This is the default UpstreamClientStrategy implementation. It issues
    synchronous HTTP requests using an injected :class:`ProviderConfig` and
    appends the provider API key to the query string when available.

    Attributes:
        config: Provider configuration with base URL, API key details, and
            default timeout.
    """

    def __init__(self, config: ProviderConfig):
        self.config = config

    def request(
        self,
        view: Any,
        method: str,
        url_path: str,
        *,
        params: Iterable[Tuple[str, str]] = (),
    ) -> httpx.Response:
        """Issue an HTTP request to the upstream provider.

        Args:
            view: The calling view. ``view.timeout`` is used when present.
            method: HTTP method name (e.g., "GET").
            url_path: The provider-relative path (already formatted).
            params: Query-string pairs to include.

        Returns:
            The HTTPX response from the upstream provider.
        """
        full_url = f"{self.config.base_url.rstrip('/')}" f"{url_path}"
        pairs: list[tuple[str, str]] = list(params)
        if self.config.api_key_value:
            pairs.append((self.config.api_key_param, self.config.api_key_value))
        timeout = getattr(view, "timeout", self.config.timeout)
        return httpx.request(method, full_url, params=pairs, timeout=timeout)
