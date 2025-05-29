from rest_framework import permissions


class DailyLimitPermission(permissions.BasePermission):

    message = "Daily request limit exceeded."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True

        if hasattr(request.user, "has_reached_daily_limit"):
            if request.user.has_reached_daily_limit():
                return False

            if hasattr(request.user, "increment_request_count"):
                request.user.increment_request_count()

        return True


class RequestTokenPermission(permissions.BasePermission):

    message = "Request token authentication required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "request_token")
        )
