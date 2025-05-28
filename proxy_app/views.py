import httpx
import asyncio
import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.conf import settings
from polygon import RESTClient, async_client
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class AsyncProxyView(APIView):
    """
    High-performance async HTTP proxy view.
    Forwards all HTTP requests to Polygon.io API with authentication.
    Use this for high concurrency (1000+ concurrent requests).
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    POLYGON_BASE_URL = 'https://api.polygon.io/v3'
    POLYGON_API_KEY = 'wLTZ8DMQ1tGnrlBQtkzcz8r6V6MadT6w'
    REQUEST_TIMEOUT = 30
    
    # Shared HTTP client for connection pooling
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get or create async HTTP client with connection pooling"""
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(cls.REQUEST_TIMEOUT),
                limits=httpx.Limits(max_keepalive_connections=100, max_connections=200),
                http2=True,
                follow_redirects=True
            )
        return cls._client
    
    async def get(self, request, *args, **kwargs):
        """Handle GET requests to Polygon.io API"""
        return await self._async_dispatch(request, *args, **kwargs)
    
    async def post(self, request, *args, **kwargs):
        """Handle POST requests to Polygon.io API"""
        return await self._async_dispatch(request, *args, **kwargs)
    
    async def _async_dispatch(self, request, *args, **kwargs):
        """Handle the actual async request forwarding"""
        path = kwargs.get('path', '')
        target_url = f"{self.POLYGON_BASE_URL}/{path}"
        
        # Add API key to query parameters
        if '?' in target_url:
            target_url += f"&apiKey={self.POLYGON_API_KEY}"
        else:
            target_url += f"?apiKey={self.POLYGON_API_KEY}"
        
        # Prepare headers for forwarding
        headers = self._prepare_headers(request)
        
        try:
            client = self.get_client()
            
            # Forward request asynchronously to Polygon.io
            async with client as session:
                response = await session.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=request.body if request.method in ['POST', 'PUT', 'PATCH'] else None,
                )
            
            # Parse response content
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return JsonResponse(
                    response.json(),
                    status=response.status_code,
                    safe=False
                )
            
            # Handle large responses with streaming
            if int(response.headers.get('content-length', 0)) > 1024 * 1024:
                return StreamingHttpResponse(
                    streaming_content=response.aiter_bytes(chunk_size=8192),
                    status=response.status_code,
                    content_type=content_type
                )
            
            return HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=content_type
            )
            
        except httpx.TimeoutException:
            logger.error(f"Timeout calling Polygon.io API: {target_url}")
            return JsonResponse({
                "error": "Gateway Timeout",
                "message": "The request to Polygon.io timed out"
            }, status=504)
        except httpx.RequestError as e:
            logger.error(f"Request error calling Polygon.io API: {target_url}: {e}")
            return JsonResponse({
                "error": "Bad Gateway",
                "message": "Failed to reach Polygon.io API"
            }, status=502)
        except Exception as e:
            logger.error(f"Unexpected error calling Polygon.io API: {target_url}: {e}")
            return JsonResponse({
                "error": "Internal Server Error",
                "message": str(e)
            }, status=500)
    
    def _prepare_headers(self, request):
        """Prepare headers for forwarding"""
        headers = {}
        exclude_headers = {
            'HOST', 'CONNECTION', 'KEEP-ALIVE', 'PROXY-AUTHENTICATE',
            'PROXY-AUTHORIZATION', 'TE', 'TRAILERS', 'UPGRADE',
            'CONTENT-LENGTH'
        }
        
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').upper()
                if header_name not in exclude_headers:
                    headers[header_name] = value
        
        if request.content_type:
            headers['Content-Type'] = request.content_type
            
        return headers

# Async helper functions
async def async_list_tickers(client, market="stocks", limit=100):
    return await sync_to_async(client.list_tickers)(market=market, limit=limit)

async def async_get_ticker_details(client, symbol):
    return await sync_to_async(client.get_ticker_details)(symbol)

async def async_list_trades(client, symbol, limit=100):
    return await sync_to_async(client.list_trades)(symbol, limit=limit)

# Specific endpoints for common Polygon.io operations
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
async def stocks_list(request):
    """Get list of stocks from Polygon.io"""
    client = RESTClient(api_key='wLTZ8DMQ1tGnrlBQtkzcz8r6V6MadT6w')
    try:
        tickers = await async_list_tickers(client)
        return JsonResponse({
            "status": "success",
            "data": [ticker.__dict__ for ticker in tickers]
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
async def stock_details(request, symbol):
    """Get detailed information about a specific stock"""
    client = RESTClient(api_key='wLTZ8DMQ1tGnrlBQtkzcz8r6V6MadT6w')
    try:
        ticker = await async_get_ticker_details(client, symbol)
        return JsonResponse({
            "status": "success",
            "data": ticker.__dict__
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
async def stock_trades(request, symbol):
    """Get recent trades for a specific stock"""
    client = RESTClient(api_key='wLTZ8DMQ1tGnrlBQtkzcz8r6V6MadT6w')
    try:
        trades = await async_list_trades(client, symbol)
        return JsonResponse({
            "status": "success",
            "data": [trade.__dict__ for trade in trades]
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

class SimpleProxyView(APIView): 
    """
    Simple synchronous HTTP proxy view.
    Use this for moderate load scenarios or simpler deployments.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    MICROSERVICE_BASE_URL = getattr(settings, 'MICROSERVICE_BASE_URL', 'http://localhost:8001')
    
    # Shared session for connection pooling
    _session = None
    
    @classmethod
    def get_session(cls):
        """Get or create requests session with connection pooling"""
        if cls._session is None:
            import requests
            cls._session = requests.Session()
            # Configure connection pooling for better performance
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=20,
                pool_maxsize=100,
                max_retries=3
            )
            cls._session.mount('http://', adapter)
            cls._session.mount('https://', adapter)
        return cls._session
    
    def dispatch(self, request, *args, **kwargs):
        """Handle synchronous request forwarding"""
        full_path = request.get_full_path()
        target_url = f"{self.MICROSERVICE_BASE_URL}{full_path}"
        
        # Prepare headers
        headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_') and key[5:].replace('_', '-').upper() not in ['HOST', 'CONNECTION']:
                headers[key[5:].replace('_', '-')] = value
        
        # Add user context
        if hasattr(request, 'user') and request.user.is_authenticated:
            headers['X-User-ID'] = str(request.user.id)
            headers['X-User-Email'] = request.user.email
        
        try:
            session = self.get_session()
            response = session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.body,
                timeout=30,
                stream=True  # Enable streaming for large responses
            )
            
            return HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'application/json')
            )
            
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            return HttpResponse("Service Unavailable", status=503) 