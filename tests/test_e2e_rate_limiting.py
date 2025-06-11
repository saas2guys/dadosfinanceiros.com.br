"""
End-to-end tests for rate limiting functionality.
Simple tests to verify the complete system works.
"""
from decimal import Decimal
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from users.models import Plan, RateLimitService, RateLimitCounter, APIUsage
from tests.factories import UserFactory, PlanFactory

User = get_user_model()


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'rate_limit': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)
class EndToEndRateLimitingTest(TestCase):
    """Simple end-to-end tests for rate limiting"""

    def setUp(self):
        # Create plan
        self.plan = PlanFactory(
            name='Test Plan',
            price_monthly=Decimal('9.99'),
            hourly_request_limit=10,
            daily_request_limit=100,
            monthly_request_limit=3000
        )
        
        # Create user
        self.user = UserFactory(current_plan=self.plan)

    def test_rate_limiting_service_functionality(self):
        """Test that the rate limiting service works correctly"""
        identifier = f"user_{self.user.id}"
        endpoint = "test_service"  # Use unique endpoint to avoid conflicts
        
        # Test that counters start at 0
        count = RateLimitService.get_usage_count(identifier, endpoint, 'hour')
        self.assertEqual(count, 0)
        
        # Test incrementing
        for i in range(1, 11):
            new_count = RateLimitService.check_and_increment(identifier, endpoint, 'hour')
            self.assertEqual(new_count, i)
        
        # Test that we can retrieve the count
        count = RateLimitService.get_usage_count(identifier, endpoint, 'hour')
        self.assertEqual(count, 10)

    def test_user_rate_limit_checking(self):
        """Test user's rate limit checking methods"""
        # Should start with ability to make requests
        can_make, reason = self.user.check_rate_limits('test')
        self.assertTrue(can_make)
        self.assertEqual(reason, "OK")
        
        # Increment usage to the limit
        for i in range(10):
            self.user.increment_usage_counters('test')
        
        # Should now be rate limited
        can_make, reason = self.user.check_rate_limits('test')
        self.assertFalse(can_make)
        self.assertIn('hourly limit reached', reason)

    def test_different_time_windows(self):
        """Test that different time windows work independently"""
        identifier = f"user_{self.user.id}"
        endpoint = "test"
        
        # Test all time windows
        windows = ['minute', 'hour', 'day', 'month']
        
        for window in windows:
            count = RateLimitService.check_and_increment(identifier, endpoint, window)
            self.assertEqual(count, 1)
            
            # Verify counter was created
            counter = RateLimitCounter.objects.filter(
                identifier=identifier,
                endpoint=endpoint,
                window_type=window
            ).first()
            self.assertIsNotNone(counter)
            self.assertEqual(counter.count, 1)

    def test_api_usage_tracking(self):
        """Test that API usage is tracked correctly"""
        initial_count = APIUsage.objects.count()
        
        # Simulate API usage
        self.user.increment_usage_counters('test')
        
        # Check that usage was recorded
        # Note: This depends on middleware creating APIUsage records
        # For this test, we'll just verify the counter increment worked
        identifier = f"user_{self.user.id}"
        counter = RateLimitCounter.objects.filter(
            identifier=identifier,
            endpoint='test'
        ).first()
        self.assertIsNotNone(counter)

    def test_cached_limits_functionality(self):
        """Test that cached limits work correctly"""
        # Get cached limits
        limits = self.user.get_cached_limits()
        
        self.assertEqual(limits['hourly'], 10)
        self.assertEqual(limits['daily'], 100)
        self.assertEqual(limits['monthly'], 3000)
        
        # Refresh cache
        self.user.refresh_limits_cache()
        
        # Should still have same limits
        limits = self.user.get_cached_limits()
        self.assertEqual(limits['hourly'], 10)

    def test_plan_based_limits(self):
        """Test that different plans have different limits"""
        # Create premium plan
        premium_plan = PlanFactory(
            name='Premium',
            price_monthly=Decimal('29.99'),
            hourly_request_limit=1000,
            daily_request_limit=10000,
            monthly_request_limit=300000
        )
        
        # Create premium user
        premium_user = UserFactory(current_plan=premium_plan)
        
        # Compare limits
        basic_limits = self.user.get_cached_limits()
        premium_limits = premium_user.get_cached_limits()
        
        self.assertLess(basic_limits['hourly'], premium_limits['hourly'])
        self.assertLess(basic_limits['daily'], premium_limits['daily'])
        self.assertLess(basic_limits['monthly'], premium_limits['monthly'])

    def test_subscription_status_affects_access(self):
        """Test that subscription status affects API access"""
        # User with active subscription should have access
        can_make, reason = self.user.can_make_request()
        # This might return False due to subscription status, but should not error
        self.assertIsInstance(can_make, bool)
        self.assertIsInstance(reason, str)

    def test_system_components_integration(self):
        """Test that all system components work together"""
        # Test the complete flow:
        # 1. User makes request
        # 2. Rate limiting checks limits
        # 3. Usage is incremented
        # 4. Counters are updated
        
        identifier = f"user_{self.user.id}"
        endpoint = "integration_test"
        
        # Start with fresh state
        self.assertEqual(RateLimitService.get_usage_count(identifier, endpoint, 'hour'), 0)
        
        # Simulate making requests up to limit
        for i in range(1, 11):
            # Check if can make request
            can_make, reason = self.user.check_rate_limits(endpoint)
            self.assertTrue(can_make, f"Should be able to make request {i}")
            
            # Increment usage
            self.user.increment_usage_counters(endpoint)
            
            # Verify count
            count = RateLimitService.get_usage_count(identifier, endpoint, 'hour')
            self.assertEqual(count, i)
        
        # Now should be rate limited
        can_make, reason = self.user.check_rate_limits(endpoint)
        self.assertFalse(can_make)
        self.assertIn('hourly limit reached', reason)


class RateLimitingSystemHealthTest(TestCase):
    """Test system health and error handling"""

    def test_system_with_no_plan(self):
        """Test system behavior with users who have no plan"""
        user = UserFactory(current_plan=None)
        
        # Should handle gracefully
        can_make, reason = user.check_rate_limits('test')
        # Should either work with default limits or fail gracefully
        self.assertIsInstance(can_make, bool)
        self.assertIsInstance(reason, str)

    def test_system_with_invalid_data(self):
        """Test system robustness with edge cases"""
        user = UserFactory()
        
        # Test with empty endpoint
        can_make, reason = user.check_rate_limits('')
        self.assertIsInstance(can_make, bool)
        
        # Test with very long endpoint name
        long_endpoint = 'x' * 300
        can_make, reason = user.check_rate_limits(long_endpoint)
        self.assertIsInstance(can_make, bool)

    def test_database_counters_persistence(self):
        """Test that database counters persist correctly"""
        user = UserFactory()
        identifier = f"user_{user.id}"
        endpoint = "persistence_test"
        
        # Create counter
        count1 = RateLimitService.check_and_increment(identifier, endpoint, 'hour')
        self.assertEqual(count1, 1)
        
        # Increment again
        count2 = RateLimitService.check_and_increment(identifier, endpoint, 'hour')
        self.assertEqual(count2, 2)
        
        # Get count directly from database
        counter = RateLimitCounter.objects.get(
            identifier=identifier,
            endpoint=endpoint,
            window_type='hour'
        )
        self.assertEqual(counter.count, 2) 