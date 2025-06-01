from django.utils import timezone
from rest_framework import permissions
from rest_framework.permissions import BasePermission


class DailyLimitPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True

        today = timezone.now().date()
        if request.user.last_request_date != today:
            request.user.reset_daily_requests()

        can_request, message = request.user.can_make_request()

        if not can_request:
            request._permission_error = message
            return False

        return True

    def get_error_message(self, request):
        return getattr(request, "_permission_error", "Request not allowed")


class RequestTokenPermission(permissions.BasePermission):
    message = "Request token authentication required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "request_token")
        )
