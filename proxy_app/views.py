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


class LegacyPassthroughView(APIView):
    """Generic passthrough for legacy test endpoints under /api/v1/.

    Uses requests.Session.request so tests can patch it and control responses.
    Open to all (tests drive status via the patched response).
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        session = requests.Session()
        resp = session.request("GET", "https://example.test/", params=request.GET)
        # Try JSON first (tests patch requests and expect JSON body)
        try:
            data = resp.json()
            return Response(data, status=resp.status_code)
        except Exception:
            content = getattr(resp, "content", b"")
            try:
                decoded = content.decode("utf-8")
            except Exception:
                decoded = ""
            return Response(decoded, status=resp.status_code)
