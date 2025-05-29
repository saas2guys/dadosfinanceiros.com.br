import logging
from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.renderers import JSONRenderer

logger = logging.getLogger(__name__)

class PolygonProxyView(APIView):
    renderer_classes = [JSONRenderer]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = settings.POLYGON_BASE_URL
        self.api_key = settings.POLYGON_API_KEY
        self.timeout = getattr(settings, 'PROXY_TIMEOUT', 30)
        self.session = requests.Session()
        self._set_authentication()
    
    def _set_authentication(self):
        if settings.ENV != 'local':
            self.authentication_classes = [JWTAuthentication]
            self.permission_classes = [IsAuthenticated]
        else:
            self.authentication_classes = []
            self.permission_classes = [AllowAny]
    
    def _get_polygon_version(self, path):
        version = 'v3'
        
        if any(endpoint in path for endpoint in [
            'aggs',
            'snapshot/locale/us/markets',
            'last/trade',
            'last/nbbo',
            'fed/vx/treasury-yields',
            'benzinga/v1/ratings',
            'grouped/locale/us/market',
        ]):
            version = 'v2'
        
        elif any(endpoint in path for endpoint in [
            'conversion',
            'open-close',
            'related-companies',
            'meta/symbols',
            'meta/exchanges',
            'historic/trades',
            'historic/quotes',
            'last/currencies',
        ]):
            version = 'v1'
            
        return version
    
    def _get_target_url(self, path):
        clean_path = path.replace('v1/', '')
        
        if clean_path.startswith('fed/') or clean_path.startswith('benzinga/'):
            return f"{self.base_url}/{clean_path}"
            
        polygon_version = self._get_polygon_version(clean_path)
        
        if 'snapshot' in clean_path and not clean_path.startswith('snapshot/locale'):
            clean_path = f"snapshot/locale/us/markets/{clean_path.split('snapshot/')[-1]}"
            
        return f"{self.base_url}/{polygon_version}/{clean_path}"
    
    def _handle_request(self, request, path):
        try:
            target_url = self._get_target_url(path)
            params = {**request.GET.dict(), 'apiKey': self.api_key}
            headers = {k: v for k, v in request.headers.items() 
                      if k.lower() not in ['host', 'connection', 'content-length', 'authorization']}
            
            logger.info(f"Forwarding {request.method} request to: {target_url}")
            logger.info(f"With params: {params}")
            
            response = self.session.request(
                method=request.method,
                url=target_url,
                params=params,
                headers=headers,
                json=request.data if request.method in ['POST', 'PUT', 'PATCH'] else None,
                timeout=self.timeout
            )
            
            logger.info(f"Response status code: {response.status_code}")
            
            return self._process_response(response)
        except requests.Timeout:
            return self._error_response("Gateway Timeout", "The request to Polygon.io timed out", status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.RequestException as e:
            return self._error_response("Bad Gateway", str(e), status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return self._error_response("Internal Server Error", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_response(self, response):
        try:
            data = response.json() if response.content else {}
            return Response(data=data, status=response.status_code)
        except ValueError:
            if response.status_code == 404:
                return self._error_response("Not Found", "The requested resource was not found", status.HTTP_404_NOT_FOUND)
            return Response(
                data={'error': 'Invalid JSON response', 'content': response.text},
                status=response.status_code
            )
    
    def _error_response(self, error, message, status_code):
        logger.error(f"{error}: {message}")
        return Response(
            {"error": error, "message": message},
            status=status_code
        )
    
    def get(self, request, path):
        return self._handle_request(request, path)
    
    def post(self, request, path):
        return self._handle_request(request, path)
    
    def put(self, request, path):
        return self._handle_request(request, path)
    
    def delete(self, request, path):
        return self._handle_request(request, path)

    def get_polygon_url(self, path):
        # Remove /v1/ prefix if present
        if path.startswith('v1/'):
            path = path[3:]
        return f"{settings.POLYGON_BASE_URL}/{path}"

    def process_request(self, request, *args, **kwargs):
        # Get the path from kwargs
        path = kwargs.get('path', '')
        
        # Build the Polygon.io URL
        polygon_url = self.get_polygon_url(path)
        
        # Get query parameters
        params = request.GET.dict()
        
        # Add the API key
        params['apiKey'] = settings.POLYGON_API_KEY
        
        try:
            # Make the request to Polygon.io
            response = requests.get(polygon_url, params=params)
            
            # Log the request
            logger.info(f"Proxy request to {polygon_url} by user {request.request_token_user.email}")
            
            # Return the response
            return Response(
                data=response.json(),
                status=response.status_code
            )
        except requests.RequestException as e:
            logger.error(f"Error proxying request to {polygon_url}: {str(e)}")
            return Response(
                {'error': 'Failed to proxy request to Polygon.io'},
                status=status.HTTP_502_BAD_GATEWAY
            )

    def get(self, request, *args, **kwargs):
        return self.process_request(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.process_request(request, *args, **kwargs)
