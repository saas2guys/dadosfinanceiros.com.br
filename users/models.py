import uuid
from datetime import datetime, timedelta, timezone as tz
from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    CANCELED = "canceled", "Canceled"
    PAST_DUE = "past_due", "Past Due"
    INCOMPLETE = "incomplete", "Incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired", "Incomplete Expired"
    TRIALING = "trialing", "Trialing"
    UNPAID = "unpaid", "Unpaid"


class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    price_yearly = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    daily_request_limit = models.PositiveIntegerField(default=1000)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    is_free = models.BooleanField(default=False)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_yearly_price_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"

    class Meta:
        ordering = ["price_monthly"]


class User(AbstractUser):
    username = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True)
    request_token = models.UUIDField(default=uuid.uuid4, unique=True)
    request_token_created = models.DateTimeField(auto_now_add=True)
    request_token_expires = models.DateTimeField(null=True, blank=True)
    token_auto_renew = models.BooleanField(default=False)
    token_validity_days = models.PositiveIntegerField(default=30)
    token_never_expires = models.BooleanField(default=False)
    daily_requests_made = models.PositiveIntegerField(default=0)
    last_request_date = models.DateField(null=True, blank=True)
    previous_tokens = models.JSONField(default=list)
    keep_token_history = models.BooleanField(default=True)

    current_plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, blank=True
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.INACTIVE,
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.current_plan:
            try:
                free_plan = Plan.objects.get(is_free=True, is_active=True)
                self.current_plan = free_plan
            except Plan.DoesNotExist:
                pass

        if not self.token_never_expires and not self.request_token_expires:
            self.request_token_expires = timezone.now() + timedelta(
                days=self.token_validity_days
            )

        super().save(*args, **kwargs)

    @property
    def daily_request_limit(self):
        return self.current_plan.daily_request_limit if self.current_plan else 100

    def is_token_expired(self):
        if self.token_never_expires:
            return False
        if not self.request_token_expires:
            return True
        return timezone.now() > self.request_token_expires

    def reset_daily_requests_if_needed(self):
        today = timezone.now().date()
        if self.last_request_date is None or self.last_request_date < today:
            self.daily_requests_made = 0
            self.last_request_date = today
            self.save(update_fields=["daily_requests_made", "last_request_date"])

    def increment_request_count(self):
        self.reset_daily_requests_if_needed()
        self.daily_requests_made += 1
        self.save(update_fields=["daily_requests_made"])

    def get_token_info(self):
        return {
            "token": str(self.request_token),
            "created": self.request_token_created,
            "expires": self.request_token_expires,
            "never_expires": self.token_never_expires,
            "auto_renew": self.token_auto_renew,
            "validity_days": self.token_validity_days,
            "is_expired": self.is_token_expired(),
        }

    def generate_new_request_token(self, save_old=True, never_expires=False):
        if save_old and self.keep_token_history:
            old_token_data = {
                "token": str(self.request_token),
                "created": self.request_token_created.isoformat()
                if self.request_token_created
                else timezone.now(),
                "expires": self.request_token_expires.isoformat()
                if self.request_token_expires
                else None,
                "revoked_at": timezone.now().isoformat(),
                "never_expires": self.token_never_expires,
            }

            if save_old:
                TokenHistory.objects.create(
                    user=self,
                    token=old_token_data["token"],
                    expires_at=datetime.fromisoformat(old_token_data["expires"])
                    if old_token_data["expires"]
                    else None,
                    is_active=False,
                    never_expires=old_token_data["never_expires"],
                )

            if isinstance(self.previous_tokens, list):
                self.previous_tokens.append(old_token_data)
            else:
                self.previous_tokens = [old_token_data]

            if len(self.previous_tokens) > 10:
                self.previous_tokens = self.previous_tokens[-10:]

        self.request_token = uuid.uuid4()
        self.request_token_created = timezone.now()
        self.token_never_expires = never_expires

        if never_expires:
            self.request_token_expires = None
        else:
            self.request_token_expires = self.request_token_created + timedelta(
                days=self.token_validity_days
            )

        self.save()

    def regenerate_request_token(
        self, save_old=True, auto_renew=None, validity_days=None
    ):
        if auto_renew is not None:
            self.token_auto_renew = auto_renew
        if validity_days is not None:
            self.token_validity_days = validity_days

        self.generate_new_request_token(save_old=save_old)

    @property
    def is_subscription_active(self):
        return (
            self.subscription_status == SubscriptionStatus.ACTIVE
            and self.subscription_expires_at
            and self.subscription_expires_at > timezone.now()
        )

    @property
    def subscription_days_remaining(self):
        if not self.subscription_expires_at:
            return 0
        remaining = self.subscription_expires_at - timezone.now()
        return max(0, remaining.days)

    def upgrade_to_plan(self, plan):
        self.current_plan = plan
        if plan.is_free:
            self.subscription_status = SubscriptionStatus.ACTIVE
            self.subscription_expires_at = None
        self.save()

    def cancel_subscription(self):
        self.subscription_status = SubscriptionStatus.CANCELED
        self.save()

    def reactivate_subscription(self):
        if self.stripe_subscription_id and self.subscription_expires_at:
            if self.subscription_expires_at > timezone.now():
                self.subscription_status = SubscriptionStatus.ACTIVE
                self.save()
                return True
        return False

    def update_subscription_from_stripe(self, stripe_data):
        status_mapping = {
            "active": SubscriptionStatus.ACTIVE,
            "canceled": SubscriptionStatus.CANCELED,
            "incomplete": SubscriptionStatus.INCOMPLETE,
            "incomplete_expired": SubscriptionStatus.INCOMPLETE_EXPIRED,
            "past_due": SubscriptionStatus.PAST_DUE,
            "trialing": SubscriptionStatus.TRIALING,
            "unpaid": SubscriptionStatus.UNPAID,
        }

        self.subscription_status = status_mapping.get(
            stripe_data.get("status"), SubscriptionStatus.INACTIVE
        )

        if "current_period_end" in stripe_data:
            self.subscription_expires_at = datetime.fromtimestamp(
                stripe_data["current_period_end"], tz=tz.utc
            )

        if "current_period_start" in stripe_data:
            self.current_period_start = datetime.fromtimestamp(
                stripe_data["current_period_start"], tz=tz.utc
            )

        if "current_period_end" in stripe_data:
            self.current_period_end = datetime.fromtimestamp(
                stripe_data["current_period_end"], tz=tz.utc
            )

        self.save()


class TokenHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="token_history"
    )
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    never_expires = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Token histories"

    def __str__(self):
        return f"Token {self.token[:8]}... for {self.user.email}"


class WaitingList(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=100, blank=True)
    use_case = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Waiting List Entry"
        verbose_name_plural = "Waiting List Entries"

    def __str__(self):
        return f"{self.email} - {self.created_at.strftime('%Y-%m-%d')}"
