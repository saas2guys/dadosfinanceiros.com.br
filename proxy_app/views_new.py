"""
Django views for the Financial Data API
"""
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .config import (
    EndpointNotFoundError,
    FinancialAPIError,
    ProviderError,
    RateLimitError,
)
from .proxy import proxy

# Set up logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class FinancialAPIView(View):
    """Main API view that handles all financial data requests"""

    def get(self, request, *args, **kwargs):
        """Handle GET requests"""
        try:
            # Extract path from request
            path = self._extract_path(request.path)

            # Get query parameters
            params = dict(request.GET.items())

            # Log the request
            logger.info(f"Processing request: {path} with params: {params}")

            # Process through proxy
            response_data = proxy.process_request(path, params)

            return JsonResponse(response_data, safe=False)

        except EndpointNotFoundError as e:
            return self._error_response("Endpoint not found", str(e), 404)
        except RateLimitError as e:
            return self._error_response("Rate limit exceeded", str(e), 429, {"retry_after": 60})
        except ProviderError as e:
            return self._error_response("Provider error", str(e), e.status_code or 500, {"provider": e.provider})
        except FinancialAPIError as e:
            return self._error_response("API error", str(e), 500)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self._error_response("Internal server error", "An unexpected error occurred", 500)

    def post(self, request, *args, **kwargs):
        """Handle POST requests (for batch operations)"""
        try:
            path = self._extract_path(request.path)

            # Parse JSON body
            try:
                body = json.loads(request.body.decode('utf-8')) if request.body else {}
            except json.JSONDecodeError:
                return self._error_response("Invalid JSON", "Request body must be valid JSON", 400)

            # Handle batch requests
            if path == "batch":
                return self._handle_batch(body)

            # Regular POST request
            logger.info(f"POST {path} - body: {body}")
            response_data = proxy.process_request(path, body)

            return JsonResponse(response_data, safe=False)

        except Exception as e:
            logger.error(f"POST error: {e}")
            return self._error_response("Internal server error", str(e), 500)

    def _extract_path(self, request_path: str) -> str:
        """Extract API path from request"""
        # Remove API prefix
        for prefix in ['/api/v1/', '/v1/']:
            if request_path.startswith(prefix):
                return request_path[len(prefix):]
        return request_path.lstrip('/')

    def _handle_batch_request(self, body: dict) -> JsonResponse:
        """Handle batch requests for multiple endpoints"""
        if "requests" not in body or not isinstance(body["requests"], list):
            return self._error_response("Invalid batch request", "'requests' must be an array", 400)

        requests_list = body["requests"]
        if len(requests_list) > 100:
            return self._error_response("Batch too large", "Maximum 100 requests per batch", 400)

        results = []
        for i, req in enumerate(requests_list):
            try:
                if "path" not in req:
                    results.append({"index": i, "error": "Missing 'path' in request"})
                    continue

                path = req["path"]
                params = req.get("params", {})

                response_data = proxy.process_request(path, params)
                results.append({"index": i, "data": response_data})

            except Exception as e:
                results.append({"index": i, "error": str(e)})

        return JsonResponse({"results": results, "total": len(results)})

    def _error_response(self, error_type: str, message: str, status_code: int, extra_data: dict = None) -> JsonResponse:
        """Create standardized error response"""
        response_data = {"error": error_type, "message": message}
        if extra_data:
            response_data.update(extra_data)
        return JsonResponse(response_data, status=status_code)


class HealthView(View):
    """Health check endpoint"""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok"}, status=200)

class EndpointsView(View):
    """Endpoint documentation"""

    def get(self, request, *args, **kwargs):
        """Return list of all available endpoints"""
        try:
            endpoints_data = proxy.get_endpoint_list()
            return JsonResponse(endpoints_data)

        except Exception as e:
            logger.error(f"Endpoints list error: {e}")
            return JsonResponse({"error": "Failed to retrieve endpoints", "message": str(e)}, status=500)


# Maintain backward compatibility with existing implementations
UnifiedFinancialAPIView = FinancialAPIView
PolygonProxyView = FinancialAPIView
