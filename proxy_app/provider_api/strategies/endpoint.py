from __future__ import annotations

import re
from enum import Enum
from typing import Any, Optional

from rest_framework import status
from rest_framework.response import Response


class CurlyPlaceholderFormatter:
    """Format upstream endpoint paths with ``{placeholder}`` tokens.

    The provider path template (e.g., ``"/v1/{symbol}/data"``) is resolved by
    looking up placeholders in URL ``kwargs`` first, then falling back to
    ``request.query_params``. Missing placeholders result in a 400 response
    describing which parameter is required.
    """

    def format(self, view: Any, request, kwargs: dict) -> tuple[str, Optional[Response]]:
        """Resolve placeholders in the view's ``endpoint_to`` path.

        Args:
            view: The DRF view instance with ``endpoint_to``.
            request: The DRF request object.
            kwargs: URL keyword arguments.

        Returns:
            A tuple ``(formatted_path, error_response)``. ``error_response`` is
            ``None`` on success or a DRF ``Response`` with 400 status when a
            required placeholder is missing.
        """
        to_raw = getattr(view, "endpoint_to", None)
        if isinstance(to_raw, Enum):
            to_raw = to_raw.value
        to_path = str(to_raw)
        placeholders = set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", to_path))
        if not placeholders:
            return to_path, None

        values: dict[str, str] = {}
        for ph in placeholders:
            if ph in kwargs:
                values[ph] = str(kwargs[ph])
                continue
            if ph in request.query_params:
                values[ph] = request.query_params.get(ph)  # type: ignore[assignment]
                continue
            return "", Response(
                {"detail": "missing required parameter for provider path", "param": ph},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return to_path.format(**values), None
