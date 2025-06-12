import logging
import time
import asyncio
from datetime import datetime, timedelta
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import caches
from django.utils import timezone
from django.db import transaction
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from .models import APIUsage, RateLimitService, PaymentFailure

logger = logging.getLogger(__name__)


class UserRequestCountMiddleware(MiddlewareMixin):
    """Legacy middleware - maintained for backward compatibility"""
    
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Reset daily requests if needed
            request.user.reset_daily_requests_if_needed()
        return None


class DatabaseRateLimitMiddleware:
    """
    ASGI-compatible database-based rate limiting middleware with multiple time windows,
    subscription awareness, and detailed usage tracking.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache = caches['rate_limit']
        
        # Check if the get_response callable is a coroutine
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)
        
        # Paths to exclude from rate limiting
        self.excluded_paths = {
            '/admin/', '/static/', '/media/', '/health/', '/ping/',
            '/api/v1/health/', '/api/v1/endpoints/'
        }
        
        # Anonymous user limits (per IP)
        self.anonymous_limits = {
            'minute': 5,
            'hour': 50,
            'day': 500
        }
        
    def __call__(self, request):
        # Process request through rate limiting
        response = self.process_request(request)
        if response:
            return response
            
        # Continue with normal request processing
        start_time = time.time()
        response = self.get_response(request)
        
        # Handle both sync and async responses
        if asyncio.iscoroutine(response):
            # If response is a coroutine, we need to await it
            async def handle_async_response():
                actual_response = await response
                # Track usage after response (async for performance)
                self.track_usage_async(request, actual_response, start_time)
                return actual_response
            return handle_async_response()
        else:
            # Track usage after response (async for performance)
            self.track_usage_async(request, response, start_time)
            return response
    
    async def __acall__(self, request):
        # Process request through rate limiting
        response = self.process_request(request)
        if response:
            return response
            
        # Continue with normal request processing
        start_time = time.time()
        response = await self.get_response(request)
        
        # Track usage after response (async for performance)
        self.track_usage_async(request, response, start_time)
        
        return response
    
    def process_request(self, request):
        """Main rate limiting logic"""
        if not self.should_rate_limit(request):
            return None
        
        # Try to authenticate the user for API requests
        user = self._authenticate_user(request)
        
        # Get user or IP identifier
        if user and user.is_authenticated:
            # Temporarily set the user for rate limiting
            original_user = request.user
            request.user = user
            result = self.check_authenticated_user_limits(request)
            request.user = original_user  # Restore original user
            return result
        else:
            return self.check_anonymous_limits(request)
    
    def _authenticate_user(self, request):
        """Attempt to authenticate user using available methods"""
        from users.authentication import RequestTokenAuthentication
        from rest_framework_simplejwt.authentication import JWTAuthentication
        
        # Check if user is already authenticated (e.g., via session)
        if hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
        
        # Try RequestTokenAuthentication
        request_token_auth = RequestTokenAuthentication()
        try:
            auth_result = request_token_auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                return user
        except Exception:
            pass
        
        # Try JWT Authentication
        jwt_auth = JWTAuthentication()
        try:
            auth_result = jwt_auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                return user
        except Exception:
            pass
        
        # Return the current user (might be anonymous)
        return request.user
    
    def should_rate_limit(self, request):
        """Determine if request should be rate limited"""
        # Skip excluded paths
        for excluded in self.excluded_paths:
            if request.path.startswith(excluded):
                return False
        
        # Check for API requests, accounting for language prefixes
        path = request.path
        # Handle language prefixes like /en/, /pt-br/, etc.
        if '/' in path[1:]:  # If there's more than just the leading slash
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[1] == 'api':
                # Path like /en/api/... or /pt-br/api/...
                pass  # This is an API request, continue to rate limiting
            elif path_parts[0] == 'api':
                # Path like /api/...
                pass  # This is an API request, continue to rate limiting  
            else:
                # Not an API request
                return False
        elif not path.startswith('/api/'):
            return False
            
        # Skip OPTIONS requests
        if request.method == 'OPTIONS':
            return False
            
        return True
    
    def check_authenticated_user_limits(self, request):
        """Check rate limits for authenticated users"""
        user = request.user
        endpoint = self.get_endpoint_name(request)
        
        # Check payment failures first
        if self.has_payment_restrictions(user):
            return self.create_payment_failure_response()
        
        # Use the enhanced rate limiting from User model
        can_proceed, reason = user.check_rate_limits(endpoint)
        
        if not can_proceed:
            return self.create_rate_limit_response(user, reason, endpoint)
        
        # Increment counters
        user.increment_usage_counters(endpoint)
        
        return None
    
    def check_anonymous_limits(self, request):
        """Check rate limits for anonymous users (by IP)"""
        ip_address = self.get_client_ip(request)
        endpoint = self.get_endpoint_name(request)
        identifier = f"ip_{ip_address}"
        
        # Check each time window
        for window_type, limit in self.anonymous_limits.items():
            usage = RateLimitService.get_usage_count(identifier, endpoint, window_type)
            if usage >= limit:
                return self.create_anonymous_rate_limit_response(ip_address, window_type, usage, limit)
        
        # Increment counters
        RateLimitService.check_and_increment(identifier, endpoint, 'minute')
        RateLimitService.check_and_increment(identifier, endpoint, 'hour')
        RateLimitService.check_and_increment(identifier, endpoint, 'day')
        
        return None
    
    def has_payment_restrictions(self, user):
        """Check if user has payment-related restrictions"""
        try:
            payment_failure = PaymentFailure.objects.get(user=user, restrictions_applied=True)
            # Apply temporary restrictions for recent payment failures
            if payment_failure.failed_at > timezone.now() - timedelta(days=7):
                return True
        except PaymentFailure.DoesNotExist:
            pass
        return False
    
    def get_endpoint_name(self, request):
        """Extract meaningful endpoint name for rate limiting"""
        path = request.path
        
        # Handle language prefixes first
        path_parts = path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[1] == 'api':
            # Path like /en/api/... or /pt-br/api/...
            path = '/' + '/'.join(path_parts[1:])  # Remove language prefix
        elif len(path_parts) >= 1 and path_parts[0] == 'api':
            # Path like /api/...
            path = '/' + '/'.join(path_parts)
        
        # Normalize API paths
        if path.startswith('/api/v1/'):
            path = path[8:]  # Remove '/api/v1/'
        elif path.startswith('/api/'):
            path = path[5:]  # Remove '/api/'
        
        # Extract base endpoint (remove specific IDs/parameters)
        path_parts = path.split('/')
        if len(path_parts) >= 1 and path_parts[0]:
            # Take first part for grouping (e.g., 'profile', 'quotes', etc.)
            return path_parts[0]
        
        return 'general'
    
    def get_client_ip(self, request):
        """Get client IP address with proxy support"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip
        
        return request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    def create_rate_limit_response(self, user, reason, endpoint):
        """Create rate limit exceeded response for authenticated users"""
        limits = user.get_cached_limits()
        
        # Get current usage for all windows
        identifier = f"user_{user.id}"
        current_usage = {
            'hourly': RateLimitService.get_usage_count(identifier, endpoint, 'hour'),
            'daily': RateLimitService.get_usage_count(identifier, endpoint, 'day'),
            'monthly': RateLimitService.get_usage_count(identifier, endpoint, 'month')
        }
        
        # Calculate retry after based on the exceeded limit
        retry_after = self.calculate_retry_after(reason)
        
        response_data = {
            'error': 'Rate limit exceeded',
            'message': f'API rate limit exceeded: {reason}',
            'limits': limits,
            'current_usage': current_usage,
            'retry_after': retry_after,
            'endpoint': endpoint,
            'user_id': user.id,
            'timestamp': timezone.now().isoformat()
        }
        
        response = JsonResponse(response_data, status=429)
        response['Retry-After'] = str(retry_after)
        response['X-RateLimit-Limit-Hourly'] = str(limits['hourly'])
        response['X-RateLimit-Limit-Daily'] = str(limits['daily'])
        response['X-RateLimit-Remaining-Hourly'] = str(max(0, limits['hourly'] - current_usage['hourly']))
        response['X-RateLimit-Remaining-Daily'] = str(max(0, limits['daily'] - current_usage['daily']))
        
        return response
    
    def create_anonymous_rate_limit_response(self, ip_address, window_type, usage, limit):
        """Create rate limit response for anonymous users"""
        retry_after = self.calculate_retry_after_anonymous(window_type)
        
        response_data = {
            'error': 'Rate limit exceeded',
            'message': f'Anonymous API rate limit exceeded: {usage}/{limit} requests per {window_type}',
            'window_type': window_type,
            'usage': usage,
            'limit': limit,
            'retry_after': retry_after,
            'ip_address': ip_address,
            'timestamp': timezone.now().isoformat(),
            'suggestion': 'Consider registering for higher rate limits'
        }
        
        response = JsonResponse(response_data, status=429)
        response['Retry-After'] = str(retry_after)

        return response

    def create_payment_failure_response(self):
        """Create response for users with payment issues"""
        response_data = {
            'error': 'Payment required',
            'message': 'API access is limited due to payment issues. Please update your payment method.',
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(response_data, status=402)  # Payment Required
    
    def calculate_retry_after(self, reason):
        """Calculate retry-after seconds based on the type of limit exceeded"""
        now = timezone.now()
        
        if 'hourly' in reason:
            # Time until next hour
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return int((next_hour - now).total_seconds())
        elif 'daily' in reason:
            # Time until next day
            next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            return int((next_day - now).total_seconds())
        elif 'monthly' in reason:
            # Time until next month
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return int((next_month - now).total_seconds())
        
        return 3600  # Default to 1 hour
    
    def calculate_retry_after_anonymous(self, window_type):
        """Calculate retry-after for anonymous users"""
        now = timezone.now()
        
        if window_type == 'minute':
            next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
            return int((next_minute - now).total_seconds())
        elif window_type == 'hour':
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return int((next_hour - now).total_seconds())
        elif window_type == 'day':
            next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            return int((next_day - now).total_seconds())
        
        return 3600  # Default to 1 hour
    
    def track_usage_async(self, request, response, start_time):
        """Track detailed usage data asynchronously"""
        try:
            # Check if response is a proper response object
            if not hasattr(response, 'status_code'):
                logger.warning(f"Response object does not have status_code attribute: {type(response)}")
                return
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Prepare usage data
            usage_data = {
                'endpoint': self.get_endpoint_name(request),
                'method': request.method,
                'response_status': response.status_code,
                'response_time_ms': response_time_ms,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],  # Truncate long user agents
                'timestamp': timezone.now(),
            }
            
            # Add user if authenticated
            if hasattr(request, 'user') and request.user.is_authenticated:
                usage_data['user'] = request.user
            
            # Create usage record (this could be made async with Celery)
            APIUsage.objects.create(**usage_data)
            
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")


class RateLimitHeaderMiddleware(MiddlewareMixin):
    """
    Middleware to add rate limiting headers to all API responses
    """
    
    def process_response(self, request, response):
        # Only add headers to API responses
        if not request.path.startswith('/api/'):
            return response
        
        # Skip if rate limiting was bypassed
        if not self.should_add_headers(request):
            return response
        
        try:
            if request.user.is_authenticated:
                self.add_authenticated_headers(request, response)
            else:
                self.add_anonymous_headers(request, response)
        except Exception as e:
            logger.error(f"Failed to add rate limit headers: {e}")
        
        return response
    
    def should_add_headers(self, request):
        """Check if we should add rate limit headers"""
        # Skip for certain paths
        excluded_paths = ['/admin/', '/static/', '/media/']
        for excluded in excluded_paths:
            if request.path.startswith(excluded):
                return False
        return True
    
    def add_authenticated_headers(self, request, response):
        """Add rate limit headers for authenticated users"""
        user = request.user
        endpoint = self.get_endpoint_name(request.path)
        limits = user.get_cached_limits()
        identifier = f"user_{user.id}"
        
        # Get current usage
        hourly_usage = RateLimitService.get_usage_count(identifier, endpoint, 'hour')
        daily_usage = RateLimitService.get_usage_count(identifier, endpoint, 'day')
        
        # Add headers
        response['X-RateLimit-Limit-Hourly'] = str(limits['hourly'])
        response['X-RateLimit-Limit-Daily'] = str(limits['daily'])
        response['X-RateLimit-Remaining-Hourly'] = str(max(0, limits['hourly'] - hourly_usage))
        response['X-RateLimit-Remaining-Daily'] = str(max(0, limits['daily'] - daily_usage))
        response['X-RateLimit-Reset-Hour'] = str(int(timezone.now().replace(minute=0, second=0, microsecond=0).timestamp()) + 3600)
        response['X-RateLimit-Reset-Day'] = str(int(timezone.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()) + 86400)
    
    def add_anonymous_headers(self, request, response):
        """Add rate limit headers for anonymous users"""
        # For anonymous users, show the base limits
        response['X-RateLimit-Limit-Hour'] = '50'
        response['X-RateLimit-Limit-Day'] = '500'
        response['X-RateLimit-Message'] = 'Register for higher limits'
    
    def get_endpoint_name(self, path):
        """Extract endpoint name from path"""
        if path.startswith('/api/v1/'):
            path = path[8:]
        elif path.startswith('/api/'):
            path = path[5:]
        
        path_parts = path.split('/')
        return path_parts[0] if path_parts else 'general'


# Utility functions for payment failure handling
def set_payment_failure_flags(user, restriction_level='limited'):
    """Set payment failure restrictions for a user"""
    PaymentFailure.objects.update_or_create(
        user=user,
        defaults={
            'failed_at': timezone.now(),
            'restrictions_applied': True,
            'restriction_level': restriction_level
        }
    )
    
    # Clear cached limits to force recalculation
    from django.core.cache import caches
    cache = caches['rate_limit']
    cache_key = f"user_limits:{user.id}"
    cache.delete(cache_key)


def clear_payment_failure_flags(user):
    """Clear payment failure restrictions for a user"""
    try:
        payment_failure = PaymentFailure.objects.get(user=user)
        payment_failure.restrictions_applied = False
        payment_failure.save()
    except PaymentFailure.DoesNotExist:
        pass
    
    # Clear cached limits
    from django.core.cache import caches
    cache = caches['rate_limit']
    cache_key = f"user_limits:{user.id}"
    cache.delete(cache_key)
