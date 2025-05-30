import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Plan(models.Model):
    """Subscription plans with different features and pricing"""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    daily_request_limit = models.IntegerField(help_text="Daily API request limit")
    price_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Monthly price in USD",
    )
    stripe_price_id = models.CharField(
        max_length=255, blank=True, null=True, help_text="Stripe Price ID for this plan"
    )
    features = models.JSONField(
        default=dict, help_text="Additional features for this plan"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price_monthly"]

    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"

    @property
    def is_free(self):
        return self.price_monthly == 0

    def get_feature(self, feature_name, default=None):
        """Get a specific feature value"""
        return self.features.get(feature_name, default)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Subscription status choices
    SUBSCRIPTION_STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("past_due", "Past Due"),
        ("canceled", "Canceled"),
        ("trialing", "Trialing"),
    ]

    username = None
    email = models.EmailField(_("email address"), unique=True)

    # Plan and subscription fields
    current_plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Current subscription plan",
    )
    subscription_status = models.CharField(
        max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default="inactive"
    )

    # Stripe integration fields
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_started_at = models.DateTimeField(null=True, blank=True)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    # API usage tracking
    daily_requests_made = models.IntegerField(default=0)
    last_request_date = models.DateField(null=True, blank=True)

    # Token management
    request_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    request_token_created = models.DateTimeField(auto_now_add=True)
    request_token_expires = models.DateTimeField(null=True, blank=True)
    token_auto_renew = models.BooleanField(default=False)
    token_validity_days = models.IntegerField(default=30)
    previous_tokens = models.JSONField(default=list, blank=True)
    keep_token_history = models.BooleanField(default=True)
    token_never_expires = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        # Set default plan for new users
        if not self.current_plan_id:
            try:
                free_plan = Plan.objects.get(slug="free")
                self.current_plan = free_plan
            except Plan.DoesNotExist:
                pass

        # Ensure request_token_created is set if not already
        if not self.request_token_created:
            self.request_token_created = timezone.now()

        # Only set expiration if token doesn't never expire and no expiration is set
        if (
            self.request_token_created
            and not self.request_token_expires
            and not self.token_never_expires
        ):
            self.request_token_expires = self.request_token_created + timedelta(
                days=self.token_validity_days
            )
        # If token should never expire, ensure expiration is None
        elif self.token_never_expires:
            self.request_token_expires = None

        super().save(*args, **kwargs)

    @property
    def daily_request_limit(self):
        """Get daily request limit from current plan"""
        if self.current_plan:
            return self.current_plan.daily_request_limit
        return 0  # No plan means no requests allowed

    @property
    def is_subscription_active(self):
        """Check if user has an active subscription"""
        if not self.current_plan:
            return False

        # Even free plans should respect subscription status
        if self.subscription_status not in ["active", "trialing"]:
            return False

        # For paid plans, also check expiration
        if not self.current_plan.is_free:
            return (
                not self.subscription_expires_at
                or self.subscription_expires_at > timezone.now()
            )

        return True

    @property
    def subscription_days_remaining(self):
        """Get days remaining in subscription"""
        if not self.subscription_expires_at:
            return None
        remaining = self.subscription_expires_at - timezone.now()
        return max(0, remaining.days)

    def can_make_request(self):
        """Check if user can make an API request"""
        if not self.is_subscription_active:
            return False, "subscription not active"

        if self.has_reached_daily_limit():
            return False, "daily request limit reached"

        return True, "OK"

    def upgrade_to_plan(self, plan):
        """Upgrade user to a new plan"""
        self.current_plan = plan
        if plan.is_free:
            self.subscription_status = "active"
            self.subscription_expires_at = None
        self.save()

    def cancel_subscription(self):
        """Cancel user's subscription"""
        self.subscription_status = "canceled"
        # Keep current plan until expiration
        self.save()

    def reactivate_subscription(self):
        """Reactivate a canceled subscription"""
        if (
            self.subscription_expires_at
            and self.subscription_expires_at > timezone.now()
        ):
            self.subscription_status = "active"
            self.save()
            return True
        return False

    def generate_new_request_token(self, save_old=True, never_expires=False):
        if save_old and self.request_token:
            # Create TokenHistory record for the old token
            TokenHistory.objects.create(
                user=self,
                token=str(self.request_token),
                expires_at=self.request_token_expires,
                is_active=False,  # Old token is now inactive
                never_expires=self.token_never_expires,
            )

            old_tokens = self.previous_tokens or []
            # Store just the token string for backward compatibility with tests
            old_tokens.append(str(self.request_token))
            # Limit history to last 20 tokens
            if len(old_tokens) > 20:
                old_tokens = old_tokens[-20:]
            self.previous_tokens = old_tokens

        self.request_token = uuid.uuid4()
        self.request_token_created = timezone.now()
        self.token_never_expires = never_expires

        if never_expires:
            self.request_token_expires = None
        else:
            self.request_token_expires = self.request_token_created + timedelta(
                days=self.token_validity_days
            )

        # Create TokenHistory record for the new token
        TokenHistory.objects.create(
            user=self,
            token=str(self.request_token),
            expires_at=self.request_token_expires,
            is_active=True,
            never_expires=never_expires,
        )

        self.save()
        return self.request_token

    def reset_daily_requests(self):
        self.daily_requests_made = 0
        self.last_request_date = timezone.now().date()
        self.save()

    def increment_request_count(self):
        self.daily_requests_made += 1
        self.last_request_date = timezone.now().date()
        self.save()

    def has_reached_daily_limit(self):
        today = timezone.now().date()
        # If it's a different date, the count should be considered reset
        if self.last_request_date != today:
            return False
        return self.daily_requests_made >= self.daily_request_limit

    def is_token_expired(self):
        if self.token_never_expires:
            return False
        if not self.request_token_expires:
            return False
        is_expired = self.request_token_expires < timezone.now()
        if is_expired and self.token_auto_renew:
            self.generate_new_request_token()
            return False
        return is_expired

    def get_token_info(self):
        token_str = str(self.request_token)
        return {
            "token": token_str,  # For API compatibility
            "request_token": token_str,  # For test compatibility
            "created": self.request_token_created,
            "expires": self.request_token_expires,
            "auto_renew": self.token_auto_renew,
            "validity_days": self.token_validity_days,
            "previous_tokens": self.previous_tokens,
            "never_expires": self.token_never_expires,
            "is_expired": self.is_token_expired(),
        }

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


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
        if self.never_expires:
            return f"{self.user.email}'s forever token ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
        return f"{self.user.email}'s token ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
