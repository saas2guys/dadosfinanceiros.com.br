import requests
from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import DailyLimitPermission


def api_documentation(request):
    return render(request, "api/docs.html")


class PolygonProxyView(APIView):
    """Legacy shim view used by tests to validate auth and permissions.

    This view is not used in production routing but provides a stable target
    for unit tests that patch `_handle_request` and `requests.Session.request`.
    It enforces authentication and daily limit permission checks.
    """

    permission_classes = [IsAuthenticated, DailyLimitPermission]

    def _handle_request(self, request):
        return Response({}, status=200)

    def get(self, request, *args, **kwargs):
        return self._handle_request(request)
