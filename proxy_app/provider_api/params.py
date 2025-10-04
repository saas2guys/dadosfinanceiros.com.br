from __future__ import annotations

from enum import Enum
from typing import Any, Iterable


class AllowedParamFilter:
    """Helpers for filtering and flattening query parameters.

    This utility provides two responsibilities:

    1) Build a set of allowed parameter keys from a specification (enum class,
       iterable of enum classes, or iterable of strings). Returning an empty
       set means "allow nothing"; returning ``None`` means "no restriction".
    2) Convert mappings or query-param-like objects into flattened
       ``(key, value)`` pairs suitable for HTTP query strings.
    """

    @staticmethod
    def build_allowed_keys(spec: Any) -> set[str] | None:
        """Build a set of allowed parameter names from a specification.

        Args:
            spec: One of the following:
                - An enum class (iterable of members with ``.value`` strings)
                - An iterable of enum classes
                - An iterable of strings

        Returns:
            A set of allowed parameter names, or ``None`` if no restriction
            is defined or the specification cannot be interpreted.
        """
        if spec is None:
            return None

        # Single Enum class
        if isinstance(spec, type) and issubclass(spec, Enum):  # type: ignore[arg-type]
            return {member.value for member in spec}  # type: ignore[misc]

        keys: set[str] = set()
        if isinstance(spec, (list, tuple, set)):
            for item in spec:
                if isinstance(item, type) and issubclass(item, Enum):
                    keys.update({member.value for member in item})  # type: ignore[misc]
                    continue
                if isinstance(item, str):
                    keys.add(item)
        return keys

    @staticmethod
    def pairs_from_mapping(mapping: dict[str, Any], *, allowed_keys: set[str] | None) -> list[tuple[str, str]]:
        """Flatten a mapping into query-string pairs while honoring allowlist.

        Args:
            mapping: Validated mapping of parameter names to values. Values may
                be scalars or lists.
            allowed_keys: A set of allowed keys, or ``None`` to allow all keys.

        Returns:
            A list of ``(key, value)`` tuples where values are coerced to
            strings and list values are expanded into multiple pairs.
        """
        pairs: list[tuple[str, str]] = []
        for key, value in mapping.items():
            if allowed_keys is not None and key not in allowed_keys:
                continue
            if isinstance(value, list):
                for item in value:
                    pairs.append((key, str(item)))
                continue
            pairs.append((key, str(value)))
        return pairs

    @staticmethod
    def pairs_from_query_params(query_params: Any, *, allowed_keys: set[str] | None) -> list[tuple[str, str]]:
        """Flatten a query-param-like object into pairs while honoring allowlist.

        Args:
            query_params: An object supporting ``keys()``, ``get()`` and
                optionally ``getlist()`` (e.g., Django/DRF ``QueryDict``).
            allowed_keys: A set of allowed keys, or ``None`` to allow all keys.

        Returns:
            A list of ``(key, value)`` tuples suitable for HTTP query strings.
        """
        pairs: list[tuple[str, str]] = []
        keys = query_params.keys() if hasattr(query_params, "keys") else []
        for key in keys:
            if allowed_keys is not None and key not in allowed_keys:
                continue
            getlist = getattr(query_params, "getlist", None)
            values: Iterable[Any]
            if callable(getlist):
                values = getlist(key)
            else:
                raw = query_params.get(key)
                values = raw if isinstance(raw, list) else [raw]
            for value in values:
                pairs.append((key, str(value)))
        return pairs
