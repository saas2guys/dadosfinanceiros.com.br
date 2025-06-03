from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User

User = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


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
