from django.contrib import admin

from .models import Plan, TokenHistory, User, WaitingList


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
        self.message_user(
            request, f"Marked {queryset.count()} entries as not notified."
        )

    mark_as_not_notified.short_description = "Mark selected entries as not notified"
