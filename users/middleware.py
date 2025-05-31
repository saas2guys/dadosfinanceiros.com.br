import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class UserRequestCountMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if self._is_proxy_request(request):
            self._increment_user_requests(request, response)
        
        return response

    def _is_proxy_request(self, request):
        return (
            request.path.startswith('/v1/') or 
            request.path.startswith('/api/v1/') or
            'polygon' in request.path.lower()
        )

    def _increment_user_requests(self, request, response):
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