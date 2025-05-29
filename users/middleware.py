from django.conf import settings
from django.http import JsonResponse
from django.urls import resolve
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status


class RequestTokenMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        return self.process_request_and_response(request)

    def process_request_and_response(self, request):

        path = request.path_info.lstrip("/")

        frontend_routes = [
            "",
            "en/",
            "pt-br/",
            "login/",
            "en/login/",
            "pt-br/login/",
            "logout/",
            "en/logout/",
            "pt-br/logout/",
            "register/",
            "en/register/",
            "pt-br/register/",
            "profile/",
            "en/profile/",
            "pt-br/profile/",
            "regenerate-token/",
            "en/regenerate-token/",
            "pt-br/regenerate-token/",
            "update-token-settings/",
            "en/update-token-settings/",
            "pt-br/update-token-settings/",
            "docs/",
            "en/docs/",
            "pt-br/docs/",
        ]

        if path in frontend_routes or path.startswith(
            ("admin/", "api/token/", "api/register/", "i18n/", "static/", "media/")
        ):
            return self.get_response(request)

        for route in frontend_routes:
            if path.startswith(route):
                return self.get_response(request)

        if not path.startswith("v1/") and not path.startswith(("en/v1/", "pt-br/v1/")):
            return self.get_response(request)

        if request.method == "OPTIONS":
            return self.get_response(request)

        request_token = request.headers.get("X-Request-Token")
        if not request_token:
            return JsonResponse(
                {"error": "Request token is required for API access"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            user = User.objects.get(request_token=request_token)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid request token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if user.request_token_expires and user.request_token_expires < timezone.now():
            return JsonResponse(
                {"error": "Request token has expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.has_reached_daily_limit():
            return JsonResponse(
                {"error": "Daily request limit exceeded"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user.increment_request_count()

        request.request_token_user = user

        response = self.get_response(request)
        return response
