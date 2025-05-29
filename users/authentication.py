from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import authentication, exceptions

User = get_user_model()


class RequestTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for request token based authentication.
    
    Clients should authenticate by passing the token key in the "X-Request-Token"
    HTTP header. For example:
    
        X-Request-Token: 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    """
    
    keyword = 'X-Request-Token'
    model = User

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        request_token = self.get_token_from_request(request)
        if not request_token:
            return None

        return self.authenticate_credentials(request_token)

    def get_token_from_request(self, request):
        """
        Extract the token from the request headers.
        """
        return request.META.get('HTTP_X_REQUEST_TOKEN')

    def authenticate_credentials(self, token):
        """
        Authenticate the token and return the user.
        """
        try:
            user = self.model.objects.get(request_token=token)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid request token.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        # Check if token is expired
        if user.request_token_expires and user.request_token_expires < timezone.now():
            if user.token_auto_renew:
                # Auto-renew the token
                user.generate_new_request_token()
            else:
                raise exceptions.AuthenticationFailed('Request token has expired.')

        return (user, token)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return self.keyword 