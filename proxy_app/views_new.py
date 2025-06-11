"""
Django views for the Financial Data API
"""
import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .proxy import proxy
from .config import FinancialAPIError, ProviderError, EndpointNotFoundError, RateLimitError

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
            logger.warning(f"Endpoint not found: {e}")
            return JsonResponse({
                "error": "Endpoint not found",
                "message": str(e),
                "available_endpoints": "/api/v1/endpoints"
            }, status=404)
            
        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded: {e}")
            return JsonResponse({
                "error": "Rate limit exceeded",
                "message": str(e),
                "retry_after": 60
            }, status=429)
            
        except ProviderError as e:
            logger.error(f"Provider error: {e}")
            return JsonResponse({
                "error": "Provider error",
                "message": str(e),
                "provider": e.provider
            }, status=e.status_code or 500)
            
        except FinancialAPIError as e:
            logger.error(f"API error: {e}")
            return JsonResponse({
                "error": "API error",
                "message": str(e)
            }, status=500)
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }, status=500)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests (for batch operations)"""
        try:
            # Parse JSON body
            try:
                body = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({
                    "error": "Invalid JSON",
                    "message": "Request body must be valid JSON"
                }, status=400)
            
            # Extract path from request
            path = self._extract_path(request.path)
            
            # Handle batch requests
            if path == "batch":
                return self._handle_batch_request(body)
            
            # For other POST endpoints, treat body as params
            response_data = proxy.process_request(path, body)
            
            return JsonResponse(response_data, safe=False)
            
        except Exception as e:
            logger.error(f"POST request error: {e}")
            return JsonResponse({
                "error": "Internal server error",
                "message": str(e)
            }, status=500)
    
    def _extract_path(self, request_path: str) -> str:
        """Extract the API path from Django request path"""
        # Remove /api/v1/ prefix
        if request_path.startswith('/api/v1/'):
            return request_path[8:]  # Remove '/api/v1/'
        elif request_path.startswith('/v1/'):
            return request_path[4:]  # Remove '/v1/' for legacy compatibility
        
        return request_path.lstrip('/')
    
    def _handle_batch_request(self, body: dict) -> JsonResponse:
        """Handle batch requests for multiple endpoints"""
        if "requests" not in body:
            return JsonResponse({
                "error": "Invalid batch request",
                "message": "Body must contain 'requests' array"
            }, status=400)
        
        requests_list = body["requests"]
        if not isinstance(requests_list, list):
            return JsonResponse({
                "error": "Invalid batch request",
                "message": "'requests' must be an array"
            }, status=400)
        
        if len(requests_list) > 100:  # Limit batch size
            return JsonResponse({
                "error": "Batch too large",
                "message": "Maximum 100 requests per batch"
            }, status=400)
        
        results = []
        for i, req in enumerate(requests_list):
            try:
                if "path" not in req:
                    results.append({
                        "index": i,
                        "error": "Missing 'path' in request"
                    })
                    continue
                
                path = req["path"]
                params = req.get("params", {})
                
                response_data = proxy.process_request(path, params)
                results.append({
                    "index": i,
                    "data": response_data
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "error": str(e)
                })
        
        return JsonResponse({
            "results": results,
            "total": len(results)
        })

class HealthView(View):
    """Health check endpoint"""
    
    def get(self, request, *args, **kwargs):
        """Return health status of the API and all providers"""
        try:
            health_status = proxy.get_health_status()
            
            # Determine HTTP status code based on health
            status_code = 200
            if health_status["status"] == "degraded":
                status_code = 206  # Partial Content
            elif health_status["status"] == "unhealthy":
                status_code = 503  # Service Unavailable
            
            return JsonResponse(health_status, status=status_code)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return JsonResponse({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": proxy._get_current_timestamp()
            }, status=503)

class EndpointsView(View):
    """Endpoint documentation"""
    
    def get(self, request, *args, **kwargs):
        """Return list of all available endpoints"""
        try:
            endpoints_data = proxy.get_endpoint_list()
            return JsonResponse(endpoints_data)
            
        except Exception as e:
            logger.error(f"Endpoints list error: {e}")
            return JsonResponse({
                "error": "Failed to retrieve endpoints",
                "message": str(e)
            }, status=500)

# Maintain backward compatibility with existing implementations
UnifiedFinancialAPIView = FinancialAPIView
PolygonProxyView = FinancialAPIView 