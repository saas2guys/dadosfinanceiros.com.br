from django.contrib import admin

from .models import (
    APIUsage,
    Feature,
    Plan,
    RateLimitCounter,
    TokenHistory,
    UsageSummary,
    User,
    WaitingList,
)


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "first_name",
        "last_name",
        "company",
        "created_at",
        "is_notified",
    ]
    list_filter = ["created_at", "is_notified", "company"]
    search_fields = ["email", "first_name", "last_name", "company"]
    readonly_fields = ["created_at"]
    list_per_page = 50
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Contact Information",
            {"fields": ("email", "first_name", "last_name", "company")},
        ),
        ("Details", {"fields": ("use_case",)}),
        ("Status", {"fields": ("is_notified", "notified_at", "created_at")}),
    )

    actions = ["mark_as_notified", "mark_as_not_notified"]

    def mark_as_notified(self, request, queryset):
        from django.utils import timezone

        queryset.update(is_notified=True, notified_at=timezone.now())
        self.message_user(request, f"Marked {queryset.count()} entries as notified.")

    mark_as_notified.short_description = "Mark selected entries as notified"

    def mark_as_not_notified(self, request, queryset):
        queryset.update(is_notified=False, notified_at=None)
        self.message_user(request, f"Marked {queryset.count()} entries as not notified.")

    mark_as_not_notified.short_description = "Mark selected entries as not notified"


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price_monthly", "is_active", "is_free", "is_metered", "created_at"]
    search_fields = ["name"]
    list_filter = ["is_active", "is_free", "is_metered"]
    ordering = ["price_monthly"]

    filter_horizontal = ('features',)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(RateLimitCounter)
class RateLimitCounterAdmin(admin.ModelAdmin):
    list_display = ["identifier", "endpoint", "window_type", "window_start", "count", "updated_at"]
    search_fields = ["identifier", "endpoint"]
    list_filter = ["window_type", "window_start"]
    ordering = ["-window_start"]


@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    list_display = ["user", "endpoint", "method", "response_status", "response_time_ms", "ip_address", "timestamp"]
    search_fields = ["user__email", "endpoint", "ip_address"]
    list_filter = ["endpoint", "method", "response_status", "date"]
    ordering = ["-timestamp"]


@admin.register(UsageSummary)
class UsageSummaryAdmin(admin.ModelAdmin):
    list_display = ["user", "ip_address", "date", "hour", "total_requests", "successful_requests", "failed_requests", "avg_response_time"]
    search_fields = ["user__email", "ip_address"]
    list_filter = ["date", "hour"]
    ordering = ["-date", "-hour"]


@admin.register(TokenHistory)
class TokenHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "created_at", "expires_at", "is_active", "never_expires"]
    search_fields = ["user__email", "token"]
    list_filter = ["is_active", "never_expires", "created_at"]
    ordering = ["-created_at"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "current_plan", "subscription_status", "is_active", "is_staff", "date_joined"]
    search_fields = ["email"]
    list_filter = ["subscription_status", "is_active", "is_staff"]
    ordering = ["-date_joined"]
