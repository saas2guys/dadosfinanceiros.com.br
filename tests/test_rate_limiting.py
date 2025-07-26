"""
Comprehensive unit tests for the rate limiting system.
"""
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import factory
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from users import tasks
from users.middleware import (
    DatabaseRateLimitMiddleware,
    RateLimitHeaderMiddleware,
    UserRequestCountMiddleware,
    clear_payment_failure_flags,
    set_payment_failure_flags,
)
from users.models import (
    APIUsage,
    PaymentFailure,
    Plan,
    RateLimitCounter,
    RateLimitService,
    SubscriptionStatus,
    UsageSummary,
)

from .factories import (
    ActiveSubscriberUserFactory,
    BasicPlanFactory,
    FreePlanFactory,
    PremiumPlanFactory,
    UserFactory,
)

User = get_user_model()


# Additional Factories for Rate Limiting Models
class RateLimitCounterFactory(factory.django.DjangoModelFactory):
    """Factory for RateLimitCounter instances."""

    class Meta:
        model = RateLimitCounter

    identifier = factory.LazyFunction(lambda: f"user_{uuid.uuid4().hex[:8]}")
    endpoint = "test-endpoint"
    window_start = factory.LazyFunction(timezone.now)
    window_type = "hour"
    count = 1


class APIUsageFactory(factory.django.DjangoModelFactory):
    """Factory for APIUsage instances."""

    class Meta:
        model = APIUsage

    user = factory.SubFactory(UserFactory)
    endpoint = "test-endpoint"
    method = "GET"
    response_status = 200
    response_time_ms = 150
    ip_address = "127.0.0.1"
    user_agent = "test-client"
    timestamp = factory.LazyFunction(timezone.now)
    hour = factory.LazyAttribute(lambda obj: obj.timestamp.hour)


class UsageSummaryFactory(factory.django.DjangoModelFactory):
    """Factory for UsageSummary instances."""

    class Meta:
        model = UsageSummary

    user = factory.SubFactory(UserFactory)
    date = factory.LazyFunction(lambda: timezone.now().date())
    hour = None  # For daily summaries
    total_requests = 10
    successful_requests = 9
    failed_requests = 1
    avg_response_time = 150.5


class PaymentFailureFactory(factory.django.DjangoModelFactory):
    """Factory for PaymentFailure instances."""

    class Meta:
        model = PaymentFailure

    user = factory.SubFactory(UserFactory)
    failed_at = factory.LazyFunction(timezone.now)
    restrictions_applied = True
    restriction_level = "warning"


class EnhancedPlanFactory(factory.django.DjangoModelFactory):
    """Factory for Plan with enhanced rate limiting fields."""

    class Meta:
        model = Plan

    name = factory.Sequence(lambda n: f"Enhanced Plan {n}")
    description = "Test plan with rate limiting"
    price_monthly = Decimal("19.99")
    daily_request_limit = 1000
    hourly_request_limit = 100
    monthly_request_limit = 30000
    burst_limit = 50
    features = factory.LazyFunction(dict)
    is_active = True
    is_free = False
    is_metered = False


class TestRateLimitCounter(TestCase):
    """Test RateLimitCounter model and related functionality."""

    def setUp(self):
        self.cache = caches['rate_limit']
        self.cache.clear()

    def test_rate_limit_counter_creation(self):
        """Test creating rate limit counter."""
        counter = RateLimitCounterFactory()
        self.assertIsInstance(counter, RateLimitCounter)
        self.assertEqual(counter.count, 1)
        self.assertEqual(counter.window_type, "hour")

    def test_unique_constraint(self):
        """Test unique constraint on identifier, endpoint, window_start, window_type."""
        counter1 = RateLimitCounterFactory()

        # Creating another with same params should be fine if different window_start
        counter2 = RateLimitCounterFactory(
            identifier=counter1.identifier,
            endpoint=counter1.endpoint,
            window_type=counter1.window_type,
            window_start=counter1.window_start + timedelta(hours=1),
        )
        self.assertNotEqual(counter1.id, counter2.id)

    def test_str_representation(self):
        """Test string representation."""
        counter = RateLimitCounterFactory(identifier="user_123", endpoint="test", count=5)
        expected = "user_123 - test - 5 (hour)"
        self.assertEqual(str(counter), expected)


class TestAPIUsage(TestCase):
    """Test APIUsage model."""

    def test_api_usage_creation(self):
        """Test creating API usage record."""
        usage = APIUsageFactory()
        self.assertIsInstance(usage, APIUsage)
        self.assertEqual(usage.method, "GET")
        self.assertEqual(usage.response_status, 200)

    def test_save_sets_hour_and_date(self):
        """Test that save method sets hour and date from timestamp."""
        timestamp = timezone.now().replace(hour=15, minute=30)
        usage = APIUsageFactory(timestamp=timestamp, hour=None, date=None)

        self.assertEqual(usage.hour, 15)
        self.assertEqual(usage.date, timestamp.date())

    def test_str_representation(self):
        """Test string representation."""
        user = UserFactory(email="test@example.com")
        usage = APIUsageFactory(user=user, endpoint="test-endpoint")
        expected = f"test@example.com - test-endpoint - {usage.timestamp}"
        self.assertEqual(str(usage), expected)

    def test_str_representation_anonymous(self):
        """Test string representation for anonymous user."""
        usage = APIUsageFactory(user=None, ip_address="192.168.1.1")
        expected = f"192.168.1.1 - test-endpoint - {usage.timestamp}"
        self.assertEqual(str(usage), expected)


class TestUsageSummary(TestCase):
    """Test UsageSummary model."""

    def test_usage_summary_creation(self):
        """Test creating usage summary."""
        summary = UsageSummaryFactory()
        self.assertIsInstance(summary, UsageSummary)
        self.assertEqual(summary.total_requests, 10)
        self.assertEqual(summary.successful_requests, 9)
        self.assertEqual(summary.failed_requests, 1)

    def test_unique_constraint(self):
        """Test unique constraint on user, ip_address, date, hour."""
        summary1 = UsageSummaryFactory()

        # Creating another with different hour should work
        summary2 = UsageSummaryFactory(
            user=summary1.user, ip_address=summary1.ip_address, date=summary1.date, hour=1 if summary1.hour != 1 else 2
        )
        self.assertNotEqual(summary1.id, summary2.id)

    def test_str_representation(self):
        """Test string representation."""
        user = UserFactory(email="test@example.com")
        summary = UsageSummaryFactory(user=user, date=timezone.now().date(), hour=15, total_requests=100)
        expected = f"test@example.com - {summary.date} 15:00 - 100 requests"
        self.assertEqual(str(summary), expected)


class TestPaymentFailure(TestCase):
    """Test PaymentFailure model."""

    def test_payment_failure_creation(self):
        """Test creating payment failure record."""
        failure = PaymentFailureFactory()
        self.assertIsInstance(failure, PaymentFailure)
        self.assertTrue(failure.restrictions_applied)
        self.assertEqual(failure.restriction_level, "warning")

    def test_str_representation(self):
        """Test string representation."""
        user = UserFactory(email="test@example.com")
        failure = PaymentFailureFactory(user=user)
        expected = f"test@example.com - Payment failed at {failure.failed_at}"
        self.assertEqual(str(failure), expected)


class TestRateLimitService(TestCase):
    """Test RateLimitService static methods."""

    def setUp(self):
        self.cache = caches['rate_limit']
        self.cache.clear()
        # Clean up any existing counters
        RateLimitCounter.objects.all().delete()

    @freeze_time("2024-01-15 14:30:00")
    def test_check_and_increment_new_counter(self):
        """Test creating new counter and incrementing."""
        count = RateLimitService.check_and_increment(identifier="user_123", endpoint="test-endpoint", window_type="hour")

        self.assertEqual(count, 1)

        # Verify counter was created
        counter = RateLimitCounter.objects.get(identifier="user_123", endpoint="test-endpoint", window_type="hour")
        self.assertEqual(counter.count, 1)
        self.assertEqual(counter.window_start, timezone.now().replace(minute=0, second=0, microsecond=0))

    @freeze_time("2024-01-15 14:30:00")
    def test_check_and_increment_existing_counter(self):
        """Test incrementing existing counter."""
        # Create initial counter
        window_start = timezone.now().replace(minute=0, second=0, microsecond=0)
        RateLimitCounterFactory(identifier="user_123", endpoint="test-endpoint", window_type="hour", window_start=window_start, count=5)

        count = RateLimitService.check_and_increment(identifier="user_123", endpoint="test-endpoint", window_type="hour")

        self.assertEqual(count, 6)

    @freeze_time("2024-01-15 14:30:00")
    def test_get_usage_count_from_database(self):
        """Test getting usage count from database."""
        window_start = timezone.now().replace(minute=0, second=0, microsecond=0)
        RateLimitCounterFactory(identifier="user_123", endpoint="test-endpoint", window_type="hour", window_start=window_start, count=10)

        count = RateLimitService.get_usage_count(identifier="user_123", endpoint="test-endpoint", window_type="hour")

        self.assertEqual(count, 10)

    @freeze_time("2024-01-15 14:30:00")
    def test_get_usage_count_nonexistent(self):
        """Test getting usage count for nonexistent counter."""
        count = RateLimitService.get_usage_count(identifier="user_nonexistent", endpoint="test-endpoint", window_type="hour")

        self.assertEqual(count, 0)

    @freeze_time("2024-01-15 14:30:00")
    def test_window_start_calculation(self):
        """Test window start calculation for different window types."""
        now = timezone.now()

        # Test minute window
        RateLimitService.check_and_increment("user_1", "test", "minute")
        counter = RateLimitCounter.objects.get(identifier="user_1", window_type="minute")
        expected_minute = now.replace(second=0, microsecond=0)
        self.assertEqual(counter.window_start, expected_minute)

        # Test day window
        RateLimitService.check_and_increment("user_2", "test", "day")
        counter = RateLimitCounter.objects.get(identifier="user_2", window_type="day")
        expected_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(counter.window_start, expected_day)

        # Test month window
        RateLimitService.check_and_increment("user_3", "test", "month")
        counter = RateLimitCounter.objects.get(identifier="user_3", window_type="month")
        expected_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(counter.window_start, expected_month)


class TestEnhancedUserModel(TestCase):
    """Test enhanced User model methods for rate limiting."""

    def setUp(self):
        self.cache = caches['rate_limit']
        self.cache.clear()
        RateLimitCounter.objects.all().delete()

    def test_get_cached_limits_fresh_cache(self):
        """Test getting cached limits when cache is fresh."""
        plan = EnhancedPlanFactory(hourly_request_limit=200, daily_request_limit=2000, monthly_request_limit=60000)
        user = UserFactory(current_plan=plan)
        user.refresh_limits_cache()

        limits = user.get_cached_limits()
        expected = {'hourly': 200, 'daily': 2000, 'monthly': 60000}
        self.assertEqual(limits, expected)

    def test_get_cached_limits_stale_cache(self):
        """Test getting cached limits when cache is stale."""
        plan = EnhancedPlanFactory(hourly_request_limit=300, daily_request_limit=3000, monthly_request_limit=90000)
        user = UserFactory(current_plan=plan)

        # Set stale cache time
        user.limits_cache_updated = timezone.now() - timedelta(hours=2)
        user.save()

        limits = user.get_cached_limits()
        expected = {'hourly': 300, 'daily': 3000, 'monthly': 90000}
        self.assertEqual(limits, expected)

        # Verify cache was refreshed
        user.refresh_from_db()
        self.assertAlmostEqual(user.limits_cache_updated, timezone.now(), delta=timedelta(seconds=5))

    def test_refresh_limits_cache(self):
        """Test refreshing limits cache."""
        plan = EnhancedPlanFactory(hourly_request_limit=150, daily_request_limit=1500, monthly_request_limit=45000)
        user = UserFactory(current_plan=plan)

        user.refresh_limits_cache()

        self.assertEqual(user.cached_hourly_limit, 150)
        self.assertEqual(user.cached_daily_limit, 1500)
        self.assertEqual(user.cached_monthly_limit, 45000)
        self.assertIsNotNone(user.limits_cache_updated)

    def test_refresh_limits_cache_no_plan(self):
        """Test refreshing limits cache with no plan."""
        user = UserFactory(current_plan=None)

        user.refresh_limits_cache()

        self.assertEqual(user.cached_hourly_limit, 10)
        self.assertEqual(user.cached_daily_limit, 100)
        self.assertEqual(user.cached_monthly_limit, 3000)

    def test_check_rate_limits_inactive_subscription(self):
        """Test rate limit check with inactive subscription."""
        user = UserFactory(subscription_status=SubscriptionStatus.CANCELED, current_plan=None)

        can_request, message = user.check_rate_limits('test-endpoint')

        self.assertFalse(can_request)
        self.assertEqual(message, "subscription not active")

    def test_check_rate_limits_free_plan(self):
        """Test rate limit check with free plan."""
        free_plan = FreePlanFactory()
        user = UserFactory(current_plan=free_plan, subscription_status=SubscriptionStatus.ACTIVE)

        can_request, message = user.check_rate_limits('test-endpoint')

        self.assertTrue(can_request)
        self.assertEqual(message, "OK")

    @freeze_time("2024-01-15 14:30:00")
    def test_check_rate_limits_hourly_exceeded(self):
        """Test rate limit check when hourly limit exceeded."""
        plan = EnhancedPlanFactory(hourly_request_limit=5)
        user = UserFactory(current_plan=plan, subscription_status=SubscriptionStatus.ACTIVE)

        # Create counter that exceeds hourly limit
        window_start = timezone.now().replace(minute=0, second=0, microsecond=0)
        RateLimitCounterFactory(
            identifier=f"user_{user.id}",
            endpoint="test-endpoint",
            window_type="hour",
            window_start=window_start,
            count=6,  # Exceeds limit of 5
        )

        can_request, message = user.check_rate_limits('test-endpoint')

        self.assertFalse(can_request)
        self.assertIn("hourly limit reached", message)

    def test_increment_usage_counters(self):
        """Test incrementing usage counters for all windows."""
        user = UserFactory()

        user.increment_usage_counters('test-endpoint')

        # Check that counters were created for all window types
        identifier = f"user_{user.id}"
        for window_type in ['hour', 'day', 'month']:
            counter = RateLimitCounter.objects.get(identifier=identifier, endpoint='test-endpoint', window_type=window_type)
            self.assertEqual(counter.count, 1)

        # Check legacy daily counter was also updated
        user.refresh_from_db()
        self.assertEqual(user.daily_requests_made, 1)


class TestEnhancedPlanModel(TestCase):
    """Test enhanced Plan model."""

    def test_enhanced_plan_fields(self):
        """Test new fields in Plan model."""
        plan = EnhancedPlanFactory(hourly_request_limit=250, monthly_request_limit=75000, burst_limit=100, is_metered=True)

        self.assertEqual(plan.hourly_request_limit, 250)
        self.assertEqual(plan.monthly_request_limit, 75000)
        self.assertEqual(plan.burst_limit, 100)
        self.assertTrue(plan.is_metered)

    def test_save_sets_is_free(self):
        """Test that save method sets is_free for zero price plans."""
        plan = Plan.objects.create(name="Test Free Plan", price_monthly=Decimal("0.00"), daily_request_limit=100)

        self.assertTrue(plan.is_free)


class TestMiddleware(TestCase):
    """Test rate limiting middleware components."""

    def setUp(self):
        self.cache = caches['rate_limit']
        self.cache.clear()
        RateLimitCounter.objects.all().delete()
        PaymentFailure.objects.all().delete()

    def test_set_payment_failure_flags(self):
        """Test setting payment failure flags."""
        user = UserFactory()

        set_payment_failure_flags(user, 'limited')

        failure = PaymentFailure.objects.get(user=user)
        self.assertEqual(failure.restriction_level, 'limited')
        self.assertTrue(failure.restrictions_applied)

    def test_clear_payment_failure_flags(self):
        """Test clearing payment failure flags."""
        user = UserFactory()
        PaymentFailureFactory(user=user)

        clear_payment_failure_flags(user)

        # Check that restrictions_applied was set to False instead of deleting the record
        failure = PaymentFailure.objects.get(user=user)
        self.assertFalse(failure.restrictions_applied)


class TestMaintenanceTasks(TestCase):
    """Test maintenance tasks."""

    def setUp(self):
        RateLimitCounter.objects.all().delete()
        APIUsage.objects.all().delete()
        UsageSummary.objects.all().delete()

    def test_cleanup_old_rate_limit_counters(self):
        """Test cleaning up old rate limit counters."""
        # Create old counter (8 days old)
        old_time = timezone.now() - timedelta(days=8)
        old_counter = RateLimitCounterFactory(window_start=old_time)

        # Create recent counter
        recent_counter = RateLimitCounterFactory()

        # Run cleanup
        deleted_count = tasks.cleanup_rate_limit_counters()

        self.assertEqual(deleted_count, 1)
        self.assertFalse(RateLimitCounter.objects.filter(id=old_counter.id).exists())
        self.assertTrue(RateLimitCounter.objects.filter(id=recent_counter.id).exists())

    def test_cleanup_old_api_usage(self):
        """Test cleaning up old API usage records."""
        # Create old usage (100 days old)
        old_time = timezone.now() - timedelta(days=100)
        old_usage = APIUsageFactory(timestamp=old_time, date=old_time.date())

        # Create recent usage
        recent_usage = APIUsageFactory()

        # Run cleanup
        deleted_count = tasks.cleanup_api_usage_data()

        self.assertEqual(deleted_count, 1)
        self.assertFalse(APIUsage.objects.filter(id=old_usage.id).exists())
        self.assertTrue(APIUsage.objects.filter(id=recent_usage.id).exists())

    @freeze_time("2024-01-15 16:00:00")
    def test_aggregate_hourly_usage(self):
        """Test aggregating hourly usage."""
        user = UserFactory()
        last_hour = timezone.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

        # Create multiple API usage records for the last hour
        for i in range(5):
            APIUsageFactory(
                user=user,
                timestamp=last_hour + timedelta(minutes=i * 10),
                date=last_hour.date(),
                response_status=200,
                response_time_ms=100 + i * 10,
            )

        # Create one failed request
        APIUsageFactory(
            user=user, timestamp=last_hour + timedelta(minutes=50), date=last_hour.date(), response_status=500, response_time_ms=200
        )

        # Run aggregation
        summary_count = tasks.update_hourly_usage_summaries()

        # Check summary was created
        self.assertGreater(summary_count, 0)
        summary = UsageSummary.objects.get(user=user, date=last_hour.date(), hour=last_hour.hour)

        self.assertEqual(summary.total_requests, 6)
        self.assertEqual(summary.successful_requests, 5)
        self.assertEqual(summary.failed_requests, 1)
        # Check avg response time with tolerance for floating point precision
        self.assertAlmostEqual(summary.avg_response_time, 133.33, places=1)


class TestManagementCommands(TransactionTestCase):
    """Test management commands."""

    def setUp(self):
        # Clear all data
        Plan.objects.all().delete()
        User.objects.all().delete()
        RateLimitCounter.objects.all().delete()

    def test_setup_rate_limiting_command(self):
        """Test setup_rate_limiting management command."""
        # Ensure no plans exist
        self.assertEqual(Plan.objects.count(), 0)

        # Run command with --create-default-plans flag
        call_command('setup_rate_limiting', '--create-default-plans')

        # Check that plans were created
        self.assertTrue(Plan.objects.filter(name='Free').exists())
        self.assertTrue(Plan.objects.filter(name='Starter').exists())
        self.assertTrue(Plan.objects.filter(name='Professional').exists())
        self.assertTrue(Plan.objects.filter(name='Enterprise').exists())

        # Check free plan is properly configured
        free_plan = Plan.objects.get(name='Free')
        self.assertTrue(free_plan.is_free)
        self.assertEqual(free_plan.price_monthly, Decimal('0.00'))

    def test_run_maintenance_tasks_hourly(self):
        """Test hourly maintenance tasks command."""
        # This should run without errors
        call_command('run_maintenance_tasks', 'hourly', '--dry-run')

    def test_run_maintenance_tasks_daily(self):
        """Test daily maintenance tasks command."""
        # This should run without errors
        call_command('run_maintenance_tasks', 'daily', '--dry-run')

    def test_run_maintenance_tasks_weekly(self):
        """Test weekly maintenance tasks command."""
        # This should run without errors
        call_command('run_maintenance_tasks', 'weekly', '--dry-run')


class TestWebhookIntegration(TestCase):
    """Test enhanced webhook functionality."""

    def setUp(self):
        PaymentFailure.objects.all().delete()

    def test_payment_failure_progressive_restrictions(self):
        """Test progressive restrictions based on payment failure frequency."""
        from users.views import handle_payment_failed

        user = ActiveSubscriberUserFactory()

        # First failure should result in warning (since count starts at 0)
        invoice_data = {'subscription': user.stripe_subscription_id}
        result = handle_payment_failed(invoice_data)

        self.assertIn('user_id', result)
        self.assertEqual(result['user_id'], user.id)

        # Check that a payment failure was created
        self.assertTrue(PaymentFailure.objects.filter(user=user).exists())
        failure = PaymentFailure.objects.get(user=user)
        self.assertEqual(failure.restriction_level, 'warning')

    def test_payment_success_clears_restrictions(self):
        """Test that successful payment clears restrictions."""
        from users.views import handle_payment_succeeded

        user = ActiveSubscriberUserFactory()
        PaymentFailureFactory(user=user)

        invoice_data = {'subscription': user.stripe_subscription_id}
        result = handle_payment_succeeded(invoice_data)

        self.assertTrue(result['payment_cleared'])
        # Check that restrictions_applied was set to False instead of deleting the record
        failure = PaymentFailure.objects.get(user=user)
        self.assertFalse(failure.restrictions_applied)


class TestPerformanceOptimizations(TestCase):
    """Test performance optimizations."""

    def setUp(self):
        self.cache = caches['rate_limit']
        self.cache.clear()

    def test_cache_usage_retrieval(self):
        """Test that usage counts are cached properly."""
        user = UserFactory()
        identifier = f"user_{user.id}"
        endpoint = "test-endpoint"

        # First call should hit database
        with self.assertNumQueries(1):
            count1 = RateLimitService.get_usage_count(identifier, endpoint, 'hour')

        # Second call should hit cache (no queries)
        with self.assertNumQueries(0):
            count2 = RateLimitService.get_usage_count(identifier, endpoint, 'hour')

        self.assertEqual(count1, count2)

    def test_bulk_operations_in_cleanup(self):
        """Test that cleanup operations use bulk deletes."""
        # Create multiple old counters
        old_time = timezone.now() - timedelta(days=8)
        for i in range(10):
            RateLimitCounterFactory(window_start=old_time)

        # This should use a single bulk delete operation
        with self.assertNumQueries(1):
            deleted_count = tasks.cleanup_rate_limit_counters()

        self.assertEqual(deleted_count, 10)
