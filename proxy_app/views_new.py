"""
Django views for health and endpoint listing.
"""
import logging

from django.http import JsonResponse
from django.views import View

# Set up logging
logger = logging.getLogger(__name__)


class HealthView(View):
    """Health check endpoint"""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok"}, status=200)


__all__ = ["HealthView"]
