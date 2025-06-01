from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class RequestTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_X_REQUEST_TOKEN")

        if not token:
            return None

        try:
            user = User.objects.get(request_token=token)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        if user.is_token_expired():
            raise AuthenticationFailed("Token has expired")

        return (user, token)

    def get_token_from_request(self, request):
        return request.META.get("HTTP_X_REQUEST_TOKEN")

    def authenticate_header(self, request):
        return "X-Request-Token"
