from __future__ import annotations

from typing import Any

from rest_framework.exceptions import ValidationError

from ..params import AllowedParamFilter


class SerializerParamBuilder:
    """Build query parameter pairs using an optional DRF serializer.

    Behavior:
      - When the view declares ``serializer_class``, validate incoming query
        params using that serializer and flatten the validated data.
      - Otherwise, accept incoming params as-is (flattening list values).
      - In both paths, apply an allowlist calculated from ``view.allowed_params``.

    Returns:
      A list of ``(key, value)`` pairs or an error envelope
      ``{"__error__": {"detail": str, "errors": serializer_errors}}`` on
      validation failure.
    """

    def build(self, view: Any, request) -> list[tuple[str, str]] | dict:
        """Build the upstream query param pairs.

        Args:
            view: The DRF view instance providing configuration fields
                (``allowed_params``, ``serializer_class``).
            request: The DRF request object holding query parameters.

        Returns:
            ``list[(str, str)]`` of flattened pairs, or an error envelope with
            serializer errors when validation fails.
        """
        allowed_keys = AllowedParamFilter.build_allowed_keys(getattr(view, "allowed_params", None))

        serializer_class = getattr(view, "serializer_class", None)
        if serializer_class:
            serializer = serializer_class(data=request.query_params)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as exc:  # align with existing error envelope
                return {"__error__": {"detail": "invalid query params", "errors": exc.detail}}
            validated: dict[str, Any] = serializer.validated_data
            return AllowedParamFilter.pairs_from_mapping(validated, allowed_keys=allowed_keys)

        return AllowedParamFilter.pairs_from_query_params(request.query_params, allowed_keys=allowed_keys)
