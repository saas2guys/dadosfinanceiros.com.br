from django.contrib import admin
from .models import (
    Plan, TokenHistory, User, WaitingList, RateLimitCounter, 
    APIUsage, UsageSummary
)


class BaseAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        # Display all fields by default
        return [field.name for field in self.model._meta.fields]


@admin.register(User)
class UserAdmin(BaseAdmin):
    pass


@admin.register(Plan)
class PlanAdmin(BaseAdmin):
    pass


@admin.register(RateLimitCounter)
class RateLimitCounterAdmin(BaseAdmin):
    pass


@admin.register(APIUsage)
class APIUsageAdmin(BaseAdmin):
    pass


@admin.register(UsageSummary)
class UsageSummaryAdmin(BaseAdmin):
    pass


@admin.register(TokenHistory)
class TokenHistoryAdmin(BaseAdmin):
    pass


@admin.register(WaitingList)
class WaitingListAdmin(BaseAdmin):
    pass