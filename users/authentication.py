from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import authentication, exceptions

User = get_user_model()


class RequestTokenAuthentication(authentication.BaseAuthentication):

    keyword = "X-Request-Token"
    model = User

    def authenticate(self, request):
        request_token = self.get_token_from_request(request)
        if not request_token:
            return None

        return self.authenticate_credentials(request_token)

    def get_token_from_request(self, request):
        return request.META.get("HTTP_X_REQUEST_TOKEN")

    def authenticate_credentials(self, token):
        try:
            user = self.model.objects.get(request_token=token)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid request token.")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted.")

        if user.request_token_expires and user.request_token_expires < timezone.now():
            if user.token_auto_renew:
                user.generate_new_request_token()
            else:
                raise exceptions.AuthenticationFailed("Request token has expired.")

        return (user, token)

    def authenticate_header(self, request):
        return self.keyword
