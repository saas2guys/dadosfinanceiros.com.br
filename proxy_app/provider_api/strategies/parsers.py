from __future__ import annotations

from typing import Any

import httpx


class JsonOrTextParser:
    """
    Default ResponseParserStrategy implementation.

    Behavior:
      - If content-type contains ``application/json``, parse JSON and, when a
        ``response_serializer_class`` is provided on the view, transform the
        JSON using that serializer.
      - Otherwise, return the raw text.

    Returns:
      A tuple of ``(data, status_code)``.
    """

    def parse(self, view: Any, resp: httpx.Response) -> tuple[Any, int]:
        content_type = resp.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            return resp.text, resp.status_code

        try:
            data = resp.json()
        except ValueError:
            return resp.text, resp.status_code

        serializer_class = getattr(view, "response_serializer_class", None)
        if not serializer_class:
            return data, resp.status_code

        serializer = serializer_class(current_view=view)
        transformed = serializer.to_representation(data)
        return transformed, resp.status_code
