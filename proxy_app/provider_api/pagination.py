from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings


class ResultsKeyPagination(PageNumberPagination):
    """Paginate list payloads or dict payloads that contain a results key.

    This paginator supports two data shapes produced by upstream providers or
    serializers:

    - A plain list of items (e.g., ``[{}, {}, ...]``)
    - A dict payload that contains a list under a configurable key (default
      ``"results"``) and may include additional metadata (e.g., ``next_url``,
      ``count``, or other fields).

    When paginating a dict payload, the list under ``results_key`` is
    paginated and the remaining top-level keys are preserved and merged into
    the paginated response.

    Attributes:
        page_size: Default page size for cases where DRF settings are not
            fully wired in unit tests. Falls back to 50 when unset.
    """

    # Ensure a default page size even when settings are not fully wired in unit tests
    page_size = api_settings.PAGE_SIZE or 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preserved: dict[str, Any] | None = None

    def paginate_queryset(self, queryset, request, view=None):  # type: ignore[override]
        """Return a single page of results, or ``None`` if not paginating.

        Dict payloads are only paginated when ``view.results_key`` is truthy
        and the dict contains a list under that key. Otherwise, defer to the
        standard behavior, which will return ``None`` for non-sequences.

        Args:
            queryset: A list or dict payload.
            request: DRF request used to access pagination params.
            view: The DRF view instance providing ``results_key`` (optional).

        Returns:
            A page object or ``None`` when pagination does not apply.
        """
        if isinstance(queryset, dict) and view is not None:
            results_key = getattr(view, "results_key", "results")
            if results_key and results_key in queryset and isinstance(queryset[results_key], list):
                items = queryset[results_key]
                self._preserved = {k: v for k, v in queryset.items() if k != results_key}
                return super().paginate_queryset(items, request, view=view)
            return None
        return super().paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):  # type: ignore[override]
        """Return a paginated response, merging preserved keys when applicable.

        Args:
            data: The paginated page data (list of items).

        Returns:
            A DRF Response with pagination fields and any preserved metadata
            from dict payloads.
        """
        base_response: Response = super().get_paginated_response(data)
        if self._preserved:
            payload = dict(base_response.data)
            payload.update(self._preserved)
            return Response(payload)
        return base_response
