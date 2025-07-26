import uuid
from datetime import datetime, timedelta
from datetime import timezone as tz

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.cache import caches
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


class Feature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    daily_request_limit = models.PositiveIntegerField(default=1000)
    hourly_request_limit = models.PositiveIntegerField(default=100)
    monthly_request_limit = models.PositiveIntegerField(default=30000)
    burst_limit = models.PositiveIntegerField(default=50)
    features = models.ManyToManyField(Feature, blank=True)
    is_active = models.BooleanField(default=True)
    is_free = models.BooleanField(default=False)
    is_metered = models.BooleanField(default=False)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_yearly_price_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.price_monthly == 0:
            self.is_free = True
        super().save(*args, **kwargs)

    def get_feature(self, feature_name, default=None):
        """Get a specific feature value from the features JSON field."""
        if isinstance(self.features, dict):
            return self.features.get(feature_name, default)
        elif isinstance(self.features, list):
            return feature_name in self.features if default is None else (feature_name in self.features or default)
        return default

    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"


class RateLimitCounter(models.Model):
    identifier = models.CharField(max_length=255, db_index=True)
    endpoint = models.CharField(max_length=200, db_index=True)
    window_start = models.DateTimeField(db_index=True)
    window_type = models.CharField(
        max_length=20, choices=[('minute', 'Minute'), ('hour', 'Hour'), ('day', 'Day'), ('month', 'Month')], default='hour'
    )
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.identifier} - {self.endpoint} - {self.count} ({self.window_type})"


def get_current_date():
    return timezone.now().date()


class APIUsage(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_index=True, null=True, blank=True)
    endpoint = models.CharField(max_length=200, db_index=True)
    method = models.CharField(max_length=10)
    response_status = models.IntegerField()
    response_time_ms = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    date = models.DateField(default=get_current_date, db_index=True)
    hour = models.IntegerField(db_index=True)

    def save(self, *args, **kwargs):
        if not self.hour:
            self.hour = self.timestamp.hour
        if not self.date:
            self.date = self.timestamp.date()
        super().save(*args, **kwargs)

    def __str__(self):
        user_info = self.user.email if self.user else self.ip_address
        return f"{user_info} - {self.endpoint} - {self.timestamp}"


class UsageSummary(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    date = models.DateField(db_index=True)
    hour = models.IntegerField(null=True, blank=True)
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_info = self.user.email if self.user else self.ip_address
        period = f"{self.date} {self.hour}:00" if self.hour is not None else str(self.date)
        return f"{user_info} - {period} - {self.total_requests} requests"


class RateLimitService:
    @staticmethod
    def check_and_increment(identifier, endpoint, window_type='hour', window_duration_seconds=3600):
        from django.core.cache import caches
        from django.db import transaction

        now = timezone.now()

        if window_type == 'minute':
            window_start = now.replace(second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d%H%M')}"
        elif window_type == 'hour':
            window_start = now.replace(minute=0, second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d%H')}"
        elif window_type == 'day':
            window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d')}"
        elif window_type == 'month':
            window_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d%H')}"
        else:
            window_start = now.replace(minute=0, second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d%H')}"

        with transaction.atomic():
            counter, created = RateLimitCounter.objects.get_or_create(
                identifier=identifier, endpoint=endpoint, window_start=window_start, window_type=window_type, defaults={'count': 1}
            )

            if not created:
                counter.count = models.F('count') + 1
                counter.save(update_fields=['count', 'updated_at'])
                counter.refresh_from_db()

        cache = caches['rate_limit']
        cache_timeout = 300 if window_type in ['minute', 'hour'] else 3600
        cache.set(cache_key, counter.count, timeout=cache_timeout)

        return counter.count

    @staticmethod
    def get_usage_count(identifier, endpoint, window_type='hour'):
        from django.core.cache import caches

        cache = caches['rate_limit']
        now = timezone.now()

        if window_type == 'minute':
            window_start = now.replace(second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d%H%M')}"
        elif window_type == 'hour':
            window_start = now.replace(minute=0, second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d%H')}"
        elif window_type == 'day':
            window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d')}"
        else:
            window_start = now.replace(minute=0, second=0, microsecond=0)
            cache_key = f"usage_{window_type}:{identifier}:{endpoint}:{window_start.strftime('%Y%m%d%H')}"

        count = cache.get(cache_key)
        if count is not None:
            return count

        try:
            counter = RateLimitCounter.objects.get(
                identifier=identifier, endpoint=endpoint, window_start=window_start, window_type=window_type
            )
            count = counter.count
        except RateLimitCounter.DoesNotExist:
            count = 0

        cache_timeout = 300 if window_type in ['minute', 'hour'] else 3600
        cache.set(cache_key, count, timeout=cache_timeout)
        return count


class UserQuerySet(models.QuerySet):
    def with_active_subscriptions(self):
        return self.filter(subscription_status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])

    def with_subscription_data(self):
        return self.select_related('current_plan')


class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class StripeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(stripe_customer_id__isnull=True).exclude(stripe_customer_id='')


class User(AbstractUser):
    username = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True)
    request_token = models.UUIDField(default=uuid.uuid4, unique=True)
    request_token_created = models.DateTimeField(auto_now_add=True)
    request_token_expires = models.DateTimeField(null=True, blank=True)
    token_auto_renew = models.BooleanField(default=False)
    token_validity_days = models.PositiveIntegerField(default=30)
    token_never_expires = models.BooleanField(default=False)
    daily_requests_made = models.IntegerField(default=0)
    last_request_date = models.DateField(null=True, blank=True)
    previous_tokens = models.JSONField(default=list)
    keep_token_history = models.BooleanField(default=True)
    payment_failed_at = models.DateTimeField(null=True, blank=True)
    payment_restrictions_applied = models.BooleanField(default=False)

    current_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.INACTIVE,
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    subscription_started_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    cached_hourly_limit = models.IntegerField(null=True, blank=True)
    cached_daily_limit = models.IntegerField(null=True, blank=True)
    cached_monthly_limit = models.IntegerField(null=True, blank=True)
    limits_cache_updated = models.DateTimeField(null=True, blank=True)

    objects = UserManager()
    stripe = StripeManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.current_plan:
            try:
                free_plan = Plan.objects.get(is_free=True, is_active=True)
                self.current_plan = free_plan
            except Plan.DoesNotExist:
                pass

        if not self.token_never_expires and not self.request_token_expires:
            self.request_token_expires = timezone.now() + timedelta(days=self.token_validity_days)

        super().save(*args, **kwargs)

    @property
    def daily_request_limit(self):
        return self.current_plan.daily_request_limit if self.current_plan else 100

    @property
    def hourly_request_limit(self):
        return self.current_plan.hourly_request_limit if self.current_plan else 10

    @property
    def monthly_request_limit(self):
        return self.current_plan.monthly_request_limit if self.current_plan else 3000

    def get_cached_limits(self):
        """Return cached limits or refresh if stale"""
        if not self.limits_cache_updated or timezone.now() - self.limits_cache_updated > timedelta(hours=1):
            self.refresh_limits_cache()

        return {
            'hourly': self.cached_hourly_limit or self.hourly_request_limit,
            'daily': self.cached_daily_limit or self.daily_request_limit,
            'monthly': self.cached_monthly_limit or self.monthly_request_limit,
        }

    def refresh_limits_cache(self):
        """Update cached limit values from plan"""
        if self.current_plan:
            self.cached_hourly_limit = self.current_plan.hourly_request_limit
            self.cached_daily_limit = self.current_plan.daily_request_limit
            self.cached_monthly_limit = self.current_plan.monthly_request_limit
        else:
            self.cached_hourly_limit = 10
            self.cached_daily_limit = 100
            self.cached_monthly_limit = 3000

        self.limits_cache_updated = timezone.now()
        self.save(update_fields=['cached_hourly_limit', 'cached_daily_limit', 'cached_monthly_limit', 'limits_cache_updated'])

    def check_rate_limits(self, endpoint='general'):
        """Check if user can make request based on multiple time windows"""
        if not self.is_subscription_active and not (self.current_plan and self.current_plan.is_free):
            return False, "subscription not active"

        limits = self.get_cached_limits()
        identifier = f"user_{self.id}"

        hourly_usage = RateLimitService.get_usage_count(identifier, endpoint, 'hour')
        if hourly_usage >= limits['hourly']:
            return False, f"hourly limit reached ({hourly_usage}/{limits['hourly']})"

        daily_usage = RateLimitService.get_usage_count(identifier, endpoint, 'day')
        if daily_usage >= limits['daily']:
            return False, f"daily limit reached ({daily_usage}/{limits['daily']})"

        monthly_usage = RateLimitService.get_usage_count(identifier, endpoint, 'month')
        if monthly_usage >= limits['monthly']:
            return False, f"monthly limit reached ({monthly_usage}/{limits['monthly']})"

        return True, "OK"

    def increment_usage_counters(self, endpoint='general'):
        """Increment usage counters for all time windows"""
        identifier = f"user_{self.id}"

        RateLimitService.check_and_increment(identifier, endpoint, 'hour')
        RateLimitService.check_and_increment(identifier, endpoint, 'day')
        RateLimitService.check_and_increment(identifier, endpoint, 'month')

        self.reset_daily_requests_if_needed()
        self.daily_requests_made += 1
        self.save(update_fields=['daily_requests_made'])

    def is_token_expired(self):
        if self.token_never_expires:
            return False
        if not self.request_token_expires:
            return True
        return timezone.now() > self.request_token_expires

    def reset_daily_requests_if_needed(self):
        today = timezone.now().date()
        if self.last_request_date is None or self.last_request_date != today:
            self.daily_requests_made = 0
            self.last_request_date = today
            self.save(update_fields=["daily_requests_made", "last_request_date"])
        elif self.daily_requests_made < 0:
            self.daily_requests_made = 0
            self.save(update_fields=["daily_requests_made"])

    def increment_request_count(self):
        self.reset_daily_requests_if_needed()
        self.daily_requests_made += 1
        self.save(update_fields=["daily_requests_made"])

    def can_make_request(self):
        """Check if user can make another API request today."""
        self.reset_daily_requests_if_needed()

        if not self.current_plan:
            return False, "no active plan"

        if self.subscription_status in [SubscriptionStatus.PAST_DUE, SubscriptionStatus.UNPAID]:
            return False, "payment required"

        if not self.is_subscription_active and not self.current_plan.is_free:
            return False, "subscription not active"

        if self.daily_requests_made >= self.daily_request_limit:
            return False, "daily request limit reached"

        return True, "OK"

    def reset_daily_requests(self):
        """Reset daily request count to 0."""
        self.daily_requests_made = 0
        self.last_request_date = timezone.now().date()
        self.save(update_fields=["daily_requests_made", "last_request_date"])

    def has_reached_daily_limit(self):
        """Check if user has reached their daily API request limit."""
        self.reset_daily_requests_if_needed()
        return self.daily_requests_made >= self.daily_request_limit

    def get_token_info(self):
        return {
            "request_token": str(self.request_token),
            "token": str(self.request_token),
            "created": self.request_token_created,
            "expires": self.request_token_expires,
            "never_expires": self.token_never_expires,
            "auto_renew": self.token_auto_renew,
            "validity_days": self.token_validity_days,
            "is_expired": self.is_token_expired(),
            "previous_tokens": self.previous_tokens,
        }

    def generate_new_request_token(self, save_old=True, never_expires=False):
        if save_old and self.keep_token_history and self.request_token:
            TokenHistory.objects.create(
                user=self,
                token=str(self.request_token),
                expires_at=self.request_token_expires,
                is_active=False,
                never_expires=self.token_never_expires,
            )

            old_token_string = str(self.request_token)
            old_token_data = {
                "token": old_token_string,
                "created": self.request_token_created.isoformat() if self.request_token_created else timezone.now().isoformat(),
                "expires": self.request_token_expires.isoformat() if self.request_token_expires else None,
                "revoked_at": timezone.now().isoformat(),
                "never_expires": self.token_never_expires,
            }

            if isinstance(self.previous_tokens, list):
                if len(self.previous_tokens) == 0 or isinstance(self.previous_tokens[0], str):
                    self.previous_tokens.append(old_token_string)
                else:
                    self.previous_tokens.append(old_token_data)
            else:
                self.previous_tokens = [old_token_string]

            if len(self.previous_tokens) > 10:
                self.previous_tokens = self.previous_tokens[-10:]

        self.request_token = uuid.uuid4()
        self.request_token_created = timezone.now()
        self.token_never_expires = never_expires

        if never_expires:
            self.request_token_expires = None
        else:
            self.request_token_expires = self.request_token_created + timedelta(days=self.token_validity_days)

        self.save()
        return self.request_token

    def regenerate_request_token(self, save_old=True, auto_renew=None, validity_days=None):
        if auto_renew is not None:
            self.token_auto_renew = auto_renew
        if validity_days is not None:
            self.token_validity_days = validity_days

        return self.generate_new_request_token(save_old=save_old)

    @property
    def is_subscription_active(self):
        if self.subscription_status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
            if not self.subscription_expires_at:
                return True

            return self.subscription_expires_at > timezone.now()
        return False

    @property
    def subscription_days_remaining(self):
        if not self.subscription_expires_at:
            return None
        remaining = self.subscription_expires_at - timezone.now()
        return max(0, remaining.days)

    def upgrade_to_plan(self, plan):
        self.current_plan = plan
        if plan.is_free:
            self.subscription_status = SubscriptionStatus.ACTIVE
            self.subscription_expires_at = None

        self.limits_cache_updated = None
        self.save()

    def cancel_subscription(self):
        self.subscription_status = SubscriptionStatus.CANCELED
        self.subscription_expires_at = None
        self.save()

    def handle_payment_failure(self):
        """
        Mark payment as failed and apply payment restrictions.
        """
        self.payment_failed_at = timezone.now()
        self.payment_restrictions_applied = True
        self.save(update_fields=["payment_failed_at", "payment_restrictions_applied"])
        self.set_payment_failure_flags()

    def handle_payment_success(self):
        """
        Clear payment failure flags and activate subscription.
        """
        self.clear_payment_failure_flags()
        self.activate_subscription()

    def set_payment_failure_flags(self):
        """Set payment failure restrictions for a user"""
        self.payment_failed_at = timezone.now()
        self.payment_restrictions_applied = True
        self.save(
            update_fields=[
                'payment_failed_at',
                'payment_restrictions_applied',
            ]
        )

        cache = caches['rate_limit']
        cache_key = f"user_limits:{self.id}"
        cache.delete(cache_key)

    def clear_payment_failure_flags(self):
        """Clear payment failure restrictions for a user"""
        self.payment_restrictions_applied = False
        self.save(
            update_fields=[
                'payment_restrictions_applied',
            ]
        )

        cache = caches['rate_limit']
        cache_key = f"user_limits:{self.id}"
        cache.delete(cache_key)

    def set_subscription_status(self, new_status):
        """
        Set the user's subscription status and save.
        """
        self.subscription_status = new_status
        self.save(update_fields=["subscription_status"])

    def activate_subscription(self):
        """
        Set the user's subscription status to active and save.
        """
        self.subscription_status = SubscriptionStatus.ACTIVE
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

        self.subscription_status = status_mapping.get(stripe_data.get("status"), SubscriptionStatus.INACTIVE)

        if "current_period_end" in stripe_data:
            self.subscription_expires_at = datetime.fromtimestamp(stripe_data["current_period_end"], tz=tz.utc)

        if "current_period_start" in stripe_data:
            self.current_period_start = datetime.fromtimestamp(stripe_data["current_period_start"], tz=tz.utc)

        if "current_period_end" in stripe_data:
            self.current_period_end = datetime.fromtimestamp(stripe_data["current_period_end"], tz=tz.utc)

        self.limits_cache_updated = None
        self.save()


class TokenHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="token_history")
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

    @property
    def is_expired(self):
        """Check if this token is expired based on its expiration date"""
        if self.never_expires:
            return False
        if not self.expires_at:
            return True
        return timezone.now() > self.expires_at

    @property
    def status_display(self):
        """Return a human-readable status for this token"""
        if not self.is_active:
            return "Revoked"
        elif self.is_expired:
            return "Expired"
        else:
            return "Active"


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
