from rest_framework import permissions
from rest_framework.permissions import BasePermission
from django.utils import timezone


class DailyLimitPermission(BasePermission):
    """
    Permission class that checks if user has an active subscription 
    and hasn't exceeded their daily request limit.
    """
    
    def has_permission(self, request, view):
        # Allow if user is not authenticated (handled by other permissions)
        if not request.user or not request.user.is_authenticated:
            return True
        
        # Reset daily count if it's a new date
        today = timezone.now().date()
        if request.user.last_request_date != today:
            request.user.reset_daily_requests()
            
        # Check if user can make a request (subscription + limits)
        can_request, message = request.user.can_make_request()
        
        if not can_request:
            # Store error message for potential use in view
            request._permission_error = message
            return False
            
        return True
    
    def get_error_message(self, request):
        """Get specific error message for the failed permission"""
        return getattr(request, '_permission_error', 'Request not allowed')


class RequestTokenPermission(permissions.BasePermission):

    message = "Request token authentication required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "request_token")
        )
