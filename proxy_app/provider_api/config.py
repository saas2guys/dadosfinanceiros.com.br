from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class ProviderConfig:
    """Immutable configuration for an upstream provider.

    Attributes:
        base_url: Base URL of the upstream API (no trailing slash required).
        api_key_param: Query parameter name for the API key.
        api_key_value: API key credential value to append to each request.
        timeout: Request timeout in seconds.
    """

    base_url: str
    api_key_param: str
    api_key_value: str
    timeout: float = 20.0
