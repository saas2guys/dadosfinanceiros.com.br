from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.urls import resolve
from rest_framework import status

class RequestTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for frontend routes and authentication endpoints
        path = request.path_info.lstrip('/')
        
        # Frontend routes to skip token check
        frontend_routes = ['', 'login/', 'logout/', 'register/', 'profile/', 'regenerate-token/', 'update-token-settings/']
        if path in frontend_routes or path.startswith(('admin/', 'api/token/', 'api/register/')):
            return self.get_response(request)

        # Check if the request is for static files
        if path.startswith(('static/', 'media/')):
            return self.get_response(request)

        # Only apply token check for API routes
        if not path.startswith('v1/') and not path.startswith('api/'):
            return self.get_response(request)

        # Get request token from header
        request_token = request.headers.get('X-Request-Token')
        if not request_token:
            return JsonResponse(
                {'error': 'Request token is required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get user by request token
        User = settings.AUTH_USER_MODEL
        try:
            user = User.objects.get(request_token=request_token)
        except User.DoesNotExist:
            return JsonResponse(
                {'error': 'Invalid request token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if token is expired (if expiration is set)
        if user.request_token_expires and user.request_token_expires < timezone.now():
            return JsonResponse(
                {'error': 'Request token has expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check daily request limit
        if user.has_reached_daily_limit():
            return JsonResponse(
                {'error': 'Daily request limit exceeded'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Increment request count
        user.increment_request_count()

        # Add user to request for use in views
        request.request_token_user = user

        response = self.get_response(request)
        return response 