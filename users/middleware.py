import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class UserRequestCountMiddleware(MiddlewareMixin):
    """
    Middleware to increment user's daily request count for successful API responses.
    Only applies to authenticated users and successful responses (2xx/3xx status codes).
    """

    def process_response(self, request, response):
        """
        Increment user's request count for successful proxy API calls.
        """
        # Only count requests to proxy endpoints
        if self._is_proxy_request(request):
            self._increment_user_requests(request, response)
        
        return response

    def _is_proxy_request(self, request):
        """Check if this is a request to a proxy endpoint"""
        return (
            request.path.startswith('/v1/') or 
            request.path.startswith('/api/v1/') or
            'polygon' in request.path.lower()
        )

    def _increment_user_requests(self, request, response):
        """Increment user's daily request count for successful responses"""
        try:
            if (
                hasattr(request, "user")
                and request.user.is_authenticated
                and 200 <= response.status_code < 400
                and hasattr(request.user, 'increment_request_count')
            ):
                request.user.increment_request_count()
                logger.debug(f"Incremented request count for user {request.user.id}")
        except Exception as e:
            logger.error(f"Error incrementing user request count: {str(e)}") 