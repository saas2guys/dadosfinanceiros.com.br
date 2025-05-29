import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.


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
    username = None
    email = models.EmailField(_("email address"), unique=True)
    request_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    request_token_created = models.DateTimeField(auto_now_add=True)
    request_token_expires = models.DateTimeField(null=True, blank=True)
    daily_request_limit = models.IntegerField(default=100)
    daily_requests_made = models.IntegerField(default=0)
    last_request_date = models.DateField(null=True, blank=True)
    token_auto_renew = models.BooleanField(default=False)
    token_validity_days = models.IntegerField(default=30)
    previous_tokens = models.JSONField(default=list, blank=True)
    keep_token_history = models.BooleanField(default=True)
    token_never_expires = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        # Set initial token expiration if not set and not a forever token
        if (
            self.request_token_created
            and not self.request_token_expires
            and not self.token_never_expires
        ):
            self.request_token_expires = self.request_token_created + timedelta(
                days=self.token_validity_days
            )
        super().save(*args, **kwargs)

    def generate_new_request_token(self, save_old=True, never_expires=False):
        """Generate a new request token with expiration."""
        if save_old and self.request_token:
            # Mark the current token as inactive in TokenHistory
            TokenHistory.objects.filter(
                user=self, token=str(self.request_token), is_active=True
            ).update(is_active=False)

            # Save the old token with its expiry date
            old_tokens = self.previous_tokens or []
            old_tokens.append(
                {
                    "token": str(self.request_token),
                    "created": (
                        self.request_token_created.isoformat()
                        if self.request_token_created
                        else None
                    ),
                    "expired": timezone.now().isoformat(),
                    "never_expires": self.token_never_expires,
                }
            )
            # Keep all tokens
            self.previous_tokens = old_tokens

        # Generate new token
        self.request_token = uuid.uuid4()
        self.request_token_created = timezone.now()
        self.token_never_expires = never_expires

        if never_expires:
            self.request_token_expires = None
        else:
            self.request_token_expires = self.request_token_created + timedelta(
                days=self.token_validity_days
            )

        # Create new TokenHistory record
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
        self.save()

    def increment_request_count(self):
        self.daily_requests_made += 1
        self.last_request_date = timezone.now().date()
        self.save()

    def has_reached_daily_limit(self):
        today = timezone.now().date()
        if self.last_request_date != today:
            self.reset_daily_requests()
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
        return {
            "request_token": str(self.request_token),
            "created": self.request_token_created,
            "expires": self.request_token_expires,
            "auto_renew": self.token_auto_renew,
            "validity_days": self.token_validity_days,
            "previous_tokens": self.previous_tokens,
            "never_expires": self.token_never_expires,
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
