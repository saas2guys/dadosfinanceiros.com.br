from rest_framework import permissions


class DailyLimitPermission(permissions.BasePermission):
    """
    Custom permission to check if user has exceeded their daily request limit.
    """
    
    message = 'Daily request limit exceeded.'
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to make this request based on daily limits.
        """
        # Allow if user is not authenticated (will be handled by authentication)
        if not request.user or not request.user.is_authenticated:
            return True
            
        # Check if user has reached daily limit
        if hasattr(request.user, 'has_reached_daily_limit'):
            if request.user.has_reached_daily_limit():
                return False
                
            # Increment request count for authenticated requests
            if hasattr(request.user, 'increment_request_count'):
                request.user.increment_request_count()
        
        return True


class RequestTokenPermission(permissions.BasePermission):
    """
    Permission class that requires request token authentication.
    Used in combination with RequestTokenAuthentication.
    """
    
    message = 'Request token authentication required.'
    
    def has_permission(self, request, view):
        """
        Check if the request was authenticated with a request token.
        """
        # Check if user was authenticated via request token
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'request_token')
        ) 