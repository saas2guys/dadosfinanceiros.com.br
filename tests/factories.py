"""
Test factories for generating consistent test data across the payment test suite.
"""
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

from users.models import Plan, TokenHistory

User = get_user_model()


class StripeObject(dict):
    """
    Mock Stripe object that behaves like real Stripe objects.
    Supports both dictionary-style and attribute-style access.
    """

    def __init__(self, *args, **kwargs):
        # If we're passed a single StripeObject, just return a copy of it
        if args and len(args) == 1 and isinstance(args[0], StripeObject) and not kwargs:
            existing_obj = args[0]
            super().__init__(existing_obj)
            for key, value in existing_obj.items():
                setattr(self, key, value)
            return

        # Handle the case where we're passed an object with attributes
        if args and len(args) == 1 and hasattr(args[0], "__dict__") and not kwargs:
            obj = args[0]
            # Convert object attributes to dictionary
            obj_dict = {}
            for attr_name in dir(obj):
                if not attr_name.startswith("_"):
                    try:
                        obj_dict[attr_name] = getattr(obj, attr_name)
                    except AttributeError:
                        pass
            super().__init__(obj_dict)
            for key, value in obj_dict.items():
                setattr(self, key, value)
        else:
            # Standard dictionary initialization
            super().__init__(*args, **kwargs)
            for key, value in dict(*args, **kwargs).items():
                setattr(self, key, value)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'"
            )

    def __setattr__(self, key, value):
        self[key] = value


class PlanFactory(factory.django.DjangoModelFactory):
    """Factory for creating Plan instances with various configurations."""

    class Meta:
        model = Plan

    name = factory.Sequence(lambda n: f"Plan {n}")
    daily_request_limit = 1000
    price_monthly = Decimal("9.99")
    stripe_price_id = factory.LazyFunction(lambda: f"price_{uuid.uuid4().hex[:16]}")
    features = factory.LazyFunction(dict)
    is_active = True


class FreePlanFactory(PlanFactory):
    """Factory for free plan."""

    name = "Free"
    daily_request_limit = 100
    price_monthly = Decimal("0.00")
    stripe_price_id = None

    class Meta:
        model = Plan
        django_get_or_create = ("name",)


class BasicPlanFactory(PlanFactory):
    """Factory for basic paid plan."""

    name = "Basic"
    daily_request_limit = 1000
    price_monthly = Decimal("9.99")

    class Meta:
        model = Plan
        django_get_or_create = ("name",)


class PremiumPlanFactory(PlanFactory):
    """Factory for premium plan."""

    name = "Premium"
    daily_request_limit = 10000
    price_monthly = Decimal("29.99")

    class Meta:
        model = Plan
        django_get_or_create = ("name",)


class EnterprisePlanFactory(PlanFactory):
    """Factory for enterprise plan."""

    name = "Enterprise"
    daily_request_limit = 100000
    price_monthly = Decimal("99.99")

    class Meta:
        model = Plan
        django_get_or_create = ("name",)


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances with various subscription states."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    # Subscription fields
    current_plan = factory.SubFactory(FreePlanFactory)
    subscription_status = "active"
    stripe_customer_id = None
    stripe_subscription_id = None
    subscription_expires_at = None

    # API usage
    daily_requests_made = 0
    last_request_date = None

    # Token fields
    request_token = factory.LazyFunction(uuid.uuid4)
    token_auto_renew = False
    token_validity_days = 30
    token_never_expires = False


class ActiveSubscriberUserFactory(UserFactory):
    """Factory for user with active subscription."""

    current_plan = factory.SubFactory(BasicPlanFactory)
    subscription_status = "active"
    stripe_customer_id = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    stripe_subscription_id = factory.LazyFunction(
        lambda: f"sub_{uuid.uuid4().hex[:16]}"
    )
    subscription_expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=30)
    )


class TrialingUserFactory(UserFactory):
    """Factory for user in trial period."""

    current_plan = factory.SubFactory(BasicPlanFactory)
    subscription_status = "trialing"
    stripe_customer_id = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    stripe_subscription_id = factory.LazyFunction(
        lambda: f"sub_{uuid.uuid4().hex[:16]}"
    )
    subscription_expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=7)
    )


class ExpiredSubscriberUserFactory(UserFactory):
    """Factory for user with expired subscription."""

    current_plan = factory.SubFactory(FreePlanFactory)
    subscription_status = "canceled"
    stripe_customer_id = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    stripe_subscription_id = None
    subscription_expires_at = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=30)
    )


class PastDueUserFactory(UserFactory):
    """Factory for user with past due subscription."""

    current_plan = factory.SubFactory(BasicPlanFactory)
    subscription_status = "past_due"
    stripe_customer_id = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    stripe_subscription_id = factory.LazyFunction(
        lambda: f"sub_{uuid.uuid4().hex[:16]}"
    )
    subscription_expires_at = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=5)
    )


class TokenHistoryFactory(factory.django.DjangoModelFactory):
    """Factory for token history entries."""

    class Meta:
        model = TokenHistory

    user = factory.SubFactory(UserFactory)
    token = factory.LazyFunction(lambda: str(uuid.uuid4()))
    created_at = factory.LazyFunction(timezone.now)
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=30))
    is_active = True
    never_expires = False


# Stripe response factories for mocking
class StripeCustomerFactory(factory.DictFactory):
    """Factory for Stripe customer response."""

    id = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    object = "customer"
    email = factory.Sequence(lambda n: f"customer{n}@example.com")
    created = factory.LazyFunction(lambda: int(timezone.now().timestamp()))
    livemode = False


class UserWithSubscriptionFactory(UserFactory):
    """Factory for user with subscription data (for webhook tests)."""

    current_plan = factory.SubFactory(BasicPlanFactory)
    subscription_status = "active"
    stripe_customer_id = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    stripe_subscription_id = factory.LazyFunction(
        lambda: f"sub_{uuid.uuid4().hex[:16]}"
    )
    subscription_expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=30)
    )


class StripeSubscriptionFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances with subscription data for webhook tests."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"subscriber{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    # Subscription fields - these are what the tests expect to access
    current_plan = factory.SubFactory(BasicPlanFactory)
    subscription_status = "active"
    stripe_customer_id = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    stripe_subscription_id = factory.LazyFunction(
        lambda: f"sub_{uuid.uuid4().hex[:16]}"
    )
    subscription_expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=30)
    )

    # API usage
    daily_requests_made = 0
    last_request_date = None

    # Token fields
    request_token = factory.LazyFunction(uuid.uuid4)
    token_auto_renew = False
    token_validity_days = 30
    token_never_expires = False


class StripeMockSubscriptionFactory(factory.DictFactory):
    """Factory for Stripe subscription API response data."""

    id = factory.LazyFunction(lambda: f"sub_{uuid.uuid4().hex[:16]}")
    object = "subscription"
    customer = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    status = "active"
    current_period_start = factory.LazyFunction(lambda: int(timezone.now().timestamp()))
    current_period_end = factory.LazyFunction(
        lambda: int((timezone.now() + timedelta(days=30)).timestamp())
    )
    created = factory.LazyFunction(lambda: int(timezone.now().timestamp()))
    trial_start = None
    trial_end = None
    canceled_at = None
    cancel_at_period_end = False


class StripePriceFactory(factory.DictFactory):
    """Factory for Stripe price response."""

    id = factory.LazyFunction(lambda: f"price_{uuid.uuid4().hex[:16]}")
    object = "price"
    currency = "usd"
    unit_amount = 999  # $9.99
    recurring = {"interval": "month", "interval_count": 1}


class StripeCheckoutSessionFactory(factory.Factory):
    """Factory for Stripe checkout session response."""

    class Meta:
        model = StripeObject

    id = factory.LazyFunction(lambda: f"cs_{uuid.uuid4().hex[:16]}")
    object = "checkout.session"
    url = factory.LazyFunction(
        lambda: f"https://checkout.stripe.com/pay/cs_{uuid.uuid4().hex[:16]}"
    )
    customer = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    mode = "subscription"
    status = "open"
    payment_status = "unpaid"
    success_url = "https://example.com/success"
    cancel_url = "https://example.com/cancel"


class StripeInvoiceFactory(factory.DictFactory):
    """Factory for Stripe invoice response."""

    id = factory.LazyFunction(lambda: f"in_{uuid.uuid4().hex[:16]}")
    object = "invoice"
    customer = factory.LazyFunction(lambda: f"cus_{uuid.uuid4().hex[:16]}")
    subscription = factory.LazyFunction(lambda: f"sub_{uuid.uuid4().hex[:16]}")
    status = "paid"
    amount_paid = 999
    currency = "usd"
    created = factory.LazyFunction(lambda: int(timezone.now().timestamp()))


class StripeWebhookEventFactory(factory.DictFactory):
    """Factory for Stripe webhook event."""

    id = factory.LazyFunction(lambda: f"evt_{uuid.uuid4().hex[:16]}")
    object = "event"
    type = "invoice.payment_succeeded"
    created = factory.LazyFunction(lambda: int(timezone.now().timestamp()))
    livemode = False
    data = factory.LazyFunction(dict)
    request = {
        "id": factory.LazyFunction(lambda: f"req_{uuid.uuid4().hex[:16]}"),
        "idempotency_key": None,
    }


# Error factories for testing failure scenarios
class StripeErrorFactory(factory.DictFactory):
    """Factory for Stripe error responses."""

    error = {
        "type": "card_error",
        "code": "card_declined",
        "message": "Your card was declined.",
        "param": None,
    }


class StripeTimeoutErrorFactory(factory.DictFactory):
    """Factory for Stripe timeout error."""

    error = {"type": "api_connection_error", "message": "Request timed out."}


class StripeInvalidRequestErrorFactory(factory.DictFactory):
    """Factory for Stripe invalid request error."""

    error = {
        "type": "invalid_request_error",
        "message": "No such customer",
        "param": "customer",
    }
