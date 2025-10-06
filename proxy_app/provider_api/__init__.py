"""Provider API package.

Avoid importing URL patterns or heavy modules at package import time to
prevent circular imports during Django/DRF settings initialization.
"""

__all__: list[str] = []
