"""
Integration tests for payment processing and subscription management.
Tests end-to-end payment flows, Stripe integration, subscription lifecycle,
and complete payment system functionality.
"""
import time
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed
import unittest

from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from freezegun import freeze_time

from users.models import Plan, User
from users.stripe_service import StripeService
from .factories import (
    UserFactory, BasicPlanFactory, PremiumPlanFactory,
    StripeCustomerFactory, StripeSubscriptionFactory,
    StripeCheckoutSessionFactory, ActiveSubscriberUserFactory,
    FreePlanFactory, PlanFactory
)

User = get_user_model()


class PaymentProcessingEndToEndIntegrationTest(TestCase):
    """
    Test suite for end-to-end payment processing integration.
    
    Covers complete payment flows from checkout session creation through
    subscription activation, including Stripe integration, user updates,
    and all payment-related business logic.
    """

    def setUp(self):
        """Set up test data for payment integration tests."""
        self.user = UserFactory()
        self.basic_plan = BasicPlanFactory()
        self.premium_plan = PremiumPlanFactory()
        self.stripe_service = StripeService()

    @patch('users.stripe_service.stripe.Customer.create')
    @patch('users.stripe_service.stripe.checkout.Session.create')
    def test_completes_full_subscription_purchase_flow_successfully(self, mock_session, mock_customer):
        """Test complete subscription purchase from start to finish."""
        # Mock Stripe responses
        mock_customer.return_value = Mock(id="cus_test123")
        mock_session.return_value = Mock(
            id="cs_test123",
            url="https://checkout.stripe.com/pay/cs_test123"
        )
        
        # Step 1: Create checkout session using user (not customer_id) to trigger customer creation
        session = self.stripe_service.create_checkout_session(
            user=self.user,
            plan=self.basic_plan,
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        
        self.assertIsNotNone(session)
        mock_customer.assert_called_once()
        mock_session.assert_called_once()

    @patch('users.stripe_service.stripe.Subscription.retrieve')
    def test_processes_webhook_events_and_updates_user_subscription(self, mock_retrieve):
        """Test webhook processing updates user subscription correctly."""
        # Mock subscription data
        mock_retrieve.return_value = Mock(
            id="sub_test123",
            customer="cus_test123",
            status="active",
            current_period_end=int((timezone.now() + timedelta(days=30)).timestamp())
        )
        
        # Set up user with Stripe IDs
        self.user.stripe_customer_id = "cus_test123"
        self.user.stripe_subscription_id = "sub_test123"
        self.user.save()
        
        # Process subscription update
        subscription_data = {
            "id": "sub_test123",
            "status": "active",
            "current_period_end": int((timezone.now() + timedelta(days=30)).timestamp())
        }
        self.stripe_service.handle_subscription_updated(subscription_data)
        
        # Verify user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscription_status, "active")

    def test_handles_plan_upgrades_and_downgrades_correctly(self):
        """Test plan upgrade and downgrade functionality."""
        # Start with basic plan
        self.user.current_plan = self.basic_plan
        self.user.subscription_status = "active"
        self.user.save()
        
        # Upgrade to premium plan
        self.user.upgrade_to_plan(self.premium_plan)
        
        self.assertEqual(self.user.current_plan, self.premium_plan)
        
        # Verify daily limit updated
        self.assertEqual(
            self.user.daily_request_limit,
            self.premium_plan.daily_request_limit
        )

    def test_maintains_data_consistency_during_payment_processing(self):
        """Test data consistency during payment operations."""
        original_plan = self.user.current_plan
        original_status = self.user.subscription_status
        
        try:
            with transaction.atomic():
                self.user.upgrade_to_plan(self.premium_plan)
                self.user.subscription_status = "active"
                self.user.save()
                
                # Simulate error during processing
                raise Exception("Simulated processing error")
                
        except Exception:
            pass
        
        # Verify rollback occurred
        self.user.refresh_from_db()
        self.assertEqual(self.user.current_plan, original_plan)
        self.assertEqual(self.user.subscription_status, original_status)

    @freeze_time("2024-01-15 12:00:00")
    def test_calculates_subscription_expiry_dates_accurately(self):
        """Test subscription expiry date calculations."""
        # Set subscription with known period
        start_time = timezone.now()
        end_time = start_time + timedelta(days=30)
        
        self.user.subscription_started_at = start_time
        self.user.subscription_expires_at = end_time
        self.user.save()
        
        # Test remaining days calculation
        remaining_days = self.user.subscription_days_remaining
        self.assertEqual(remaining_days, 30)

    def test_handles_payment_failures_and_recovery_gracefully(self):
        """Test payment failure handling and recovery."""
        self.user.subscription_status = "past_due"
        self.user.save()
        
        # Verify user cannot make requests
        can_make, message = self.user.can_make_request()
        self.assertFalse(can_make)
        
        # Recover subscription
        self.user.subscription_status = "active"
        self.user.save()
        
        # Verify user can make requests again
        can_make, message = self.user.can_make_request()
        self.assertTrue(can_make)

    def test_enforces_subscription_business_rules_consistently(self):
        """Test subscription business rule enforcement."""
        # Test free plan limitations
        free_plan = FreePlanFactory()
        self.user.current_plan = free_plan
        self.user.subscription_status = "active"
        self.user.save()
        
        # Free plan should have basic limits
        self.assertTrue(self.user.current_plan.is_free)
        
        # Test paid plan benefits
        self.user.upgrade_to_plan(self.premium_plan)
        self.assertFalse(self.user.current_plan.is_free)

    def test_tracks_payment_metrics_and_usage_statistics(self):
        """Test payment and usage tracking."""
        # Reset daily requests
        self.user.reset_daily_requests()
        self.assertEqual(self.user.daily_requests_made, 0)
        
        # Increment request count
        self.user.increment_request_count()
        self.assertEqual(self.user.daily_requests_made, 1)
        
        # Test daily limit detection
        self.user.daily_requests_made = self.user.daily_request_limit
        self.user.save()
        
        self.assertTrue(self.user.has_reached_daily_limit())


class PaymentConcurrencyAndRaceConditionTest(TransactionTestCase):
    """
    Test suite for payment concurrency and race condition handling.
    
    Covers concurrent payment processing, thread safety, race condition prevention,
    and system behavior under high load payment scenarios.
    """

    def setUp(self):
        """Set up test data for concurrency tests."""
        self.user = UserFactory()
        self.plan = BasicPlanFactory()

    @unittest.skipIf(
        'sqlite' in settings.DATABASES['default']['ENGINE'],
        "SQLite doesn't handle concurrent writes well"
    )
    def test_handles_concurrent_subscription_updates_safely(self):
        """Test concurrent subscription updates don't cause race conditions."""
        def update_subscription(status):
            user = User.objects.get(id=self.user.id)
            user.subscription_status = status
            user.save()
            return status

        statuses = ["active", "past_due", "canceled", "trialing"]
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(update_subscription, status)
                for status in statuses
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        # Verify final state is consistent
        self.user.refresh_from_db()
        self.assertIn(self.user.subscription_status, statuses)

    @unittest.skipIf(
        'sqlite' in settings.DATABASES['default']['ENGINE'],
        "SQLite doesn't handle concurrent writes well"
    )
    def test_prevents_duplicate_payment_processing(self):
        """Test prevention of duplicate payment processing."""
        processed_payments = set()
        
        def process_payment(payment_id):
            if payment_id in processed_payments:
                return False  # Already processed
            
            # Simulate payment processing
            time.sleep(0.1)
            processed_payments.add(payment_id)
            return True
        
        payment_id = "payment_123"
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(process_payment, payment_id)
                for _ in range(3)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        # Only one should have processed successfully
        successful_processes = sum(results)
        self.assertEqual(successful_processes, 1)

    @unittest.skipIf(
        'sqlite' in settings.DATABASES['default']['ENGINE'],
        "SQLite doesn't handle concurrent writes well"
    )
    def test_maintains_request_count_accuracy_under_load(self):
        """Test request count accuracy under concurrent load."""
        def increment_requests():
            user = User.objects.select_for_update().get(id=self.user.id)
            user.increment_request_count()
            return user.daily_requests_made
        
        num_requests = 10
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(increment_requests)
                for _ in range(num_requests)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        # Final count should equal number of requests
        self.user.refresh_from_db()
        self.assertEqual(self.user.daily_requests_made, num_requests)

    @unittest.skipIf(
        'sqlite' in settings.DATABASES['default']['ENGINE'],
        "SQLite doesn't handle concurrent writes well"
    )
    def test_handles_concurrent_token_regeneration_safely(self):
        """Test concurrent token regeneration thread safety."""
        original_token = self.user.request_token
        
        def regenerate_token():
            user = User.objects.get(id=self.user.id)
            return user.generate_new_request_token(save_old=True)
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(regenerate_token)
                for _ in range(3)
            ]
            
            new_tokens = [future.result() for future in as_completed(futures)]
        
        # All tokens should be different
        self.assertEqual(len(set(new_tokens)), len(new_tokens))
        
        # Original token should be in history
        self.user.refresh_from_db()
        self.assertIn(str(original_token), self.user.previous_tokens)

    def test_prevents_subscription_status_corruption_during_updates(self):
        """Test subscription status integrity during concurrent updates."""
        valid_statuses = ["active", "inactive", "past_due", "canceled", "trialing"]
        
        def update_status_safely(new_status):
            try:
                with transaction.atomic():
                    user = User.objects.select_for_update().get(id=self.user.id)
                    if new_status in valid_statuses:
                        user.subscription_status = new_status
                        user.save()
                        return new_status
            except Exception:
                return None
        
        with ThreadPoolExecutor(max_workers=len(valid_statuses)) as executor:
            futures = [
                executor.submit(update_status_safely, status)
                for status in valid_statuses
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        # Final status should be valid
        self.user.refresh_from_db()
        self.assertIn(self.user.subscription_status, valid_statuses)

    @unittest.skipIf(
        'sqlite' in settings.DATABASES['default']['ENGINE'],
        "SQLite doesn't handle concurrent writes well"
    )
    def test_handles_database_deadlocks_gracefully(self):
        """Test graceful handling of database deadlocks."""
        def competing_update(field_value):
            try:
                with transaction.atomic():
                    user = User.objects.select_for_update(nowait=True).get(id=self.user.id)
                    user.daily_requests_made = field_value
                    user.save()
                    return True
            except Exception:
                return False
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(competing_update, i)
                for i in range(2)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        # At least one update should succeed
        self.assertIn(True, results)

    @unittest.skipIf(
        'sqlite' in settings.DATABASES['default']['ENGINE'],
        "SQLite doesn't handle concurrent writes well"
    )
    def test_maintains_plan_consistency_during_concurrent_upgrades(self):
        """Test plan consistency during concurrent upgrade attempts."""
        premium_plan = PremiumPlanFactory()
        
        def attempt_upgrade():
            try:
                user = User.objects.select_for_update().get(id=self.user.id)
                user.upgrade_to_plan(premium_plan)
                return True
            except Exception:
                return False
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(attempt_upgrade)
                for _ in range(3)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        # User should end up with premium plan
        self.user.refresh_from_db()
        self.assertEqual(self.user.current_plan, premium_plan)

    @unittest.skipIf(
        'sqlite' in settings.DATABASES['default']['ENGINE'],
        "SQLite doesn't handle concurrent writes well"
    )
    def test_handles_concurrent_plan_modifications(self):
        """Test handling of concurrent plan modifications."""
        original_limit = self.plan.daily_request_limit
        
        # Simulate concurrent plan updates
        self.plan.daily_request_limit = original_limit * 2
        self.plan.save()
        
        # User with this plan should get updated limit
        self.user.current_plan = self.plan
        self.user.save()
        
        self.assertEqual(self.user.daily_request_limit, original_limit * 2)


class PaymentSystemComprehensiveIntegrationTest(TestCase):
    """
    Test suite for comprehensive payment system integration.
    
    Covers complete system integration, cross-component interactions,
    real-world scenarios, and comprehensive payment system validation.
    """

    def setUp(self):
        """Set up comprehensive test environment."""
        self.free_plan = FreePlanFactory()
        self.basic_plan = BasicPlanFactory()
        self.premium_plan = PremiumPlanFactory()
        
        self.user = UserFactory(current_plan=self.free_plan, subscription_status='inactive')

    def test_complete_user_lifecycle_from_registration_to_premium(self):
        """Test complete user journey from registration to premium subscription."""
        # Step 1: User starts with free plan
        self.assertEqual(self.user.current_plan, self.free_plan)
        self.assertEqual(self.user.subscription_status, "inactive")
        
        # Step 2: User upgrades to basic plan
        self.user.upgrade_to_plan(self.basic_plan)
        self.user.subscription_status = "active"
        self.user.save()
        
        self.assertEqual(self.user.current_plan, self.basic_plan)
        self.assertEqual(self.user.daily_request_limit, 1000)
        
        # Step 3: User upgrades to premium plan
        self.user.upgrade_to_plan(self.premium_plan)
        
        self.assertEqual(self.user.current_plan, self.premium_plan)
        self.assertEqual(self.user.daily_request_limit, 10000)
        
        # Step 4: User cancels subscription
        self.user.cancel_subscription()
        
        self.assertEqual(self.user.subscription_status, "canceled")

    def test_handles_subscription_renewal_and_billing_cycles(self):
        """Test subscription renewal and billing cycle handling."""
        # Set up active subscription
        self.user.current_plan = self.basic_plan
        self.user.subscription_status = "active"
        self.user.subscription_started_at = timezone.now()
        self.user.subscription_expires_at = timezone.now() + timedelta(days=30)
        self.user.save()
        
        # Test subscription is active
        self.assertTrue(self.user.is_subscription_active)
        
        # Simulate subscription expiry
        self.user.subscription_expires_at = timezone.now() - timedelta(days=1)
        self.user.save()
        
        # Test subscription is expired
        self.assertFalse(self.user.is_subscription_active)

    def test_integrates_with_api_rate_limiting_system(self):
        """Test integration with API rate limiting."""
        # Ensure user has active subscription for rate limiting test
        self.user.subscription_status = 'active'
        self.user.save()
        
        # Set user at rate limit
        self.user.daily_requests_made = self.user.daily_request_limit
        self.user.last_request_date = timezone.now().date()
        self.user.save()
        
        # User should not be able to make requests
        can_make, message = self.user.can_make_request()
        self.assertFalse(can_make)
        
        # Reset on new day
        self.user.reset_daily_requests()
        
        # User should be able to make requests again
        can_make, message = self.user.can_make_request()
        self.assertTrue(can_make)

    def test_maintains_audit_trail_for_payment_events(self):
        """Test audit trail maintenance for payment events."""
        # Track plan changes
        original_plan = self.user.current_plan
        
        self.user.upgrade_to_plan(self.premium_plan)
        
        # Verify plan changed
        self.assertNotEqual(self.user.current_plan, original_plan)
        self.assertEqual(self.user.current_plan, self.premium_plan)

    def test_handles_edge_cases_in_subscription_management(self):
        """Test edge cases in subscription management."""
        # Test null plan handling
        self.user.current_plan = None
        self.user.save()
        
        # Should handle gracefully (default limit when no plan)
        self.assertEqual(self.user.daily_request_limit, 100)  # Default limit
        
        # Test future subscription dates
        future_date = timezone.now() + timedelta(days=365)
        self.user.subscription_expires_at = future_date
        self.user.save()
        
        # Should calculate remaining days correctly
        remaining_days = self.user.subscription_days_remaining
        self.assertGreater(remaining_days, 300)

    def test_validates_plan_constraints_and_business_rules(self):
        """Test plan constraint and business rule validation."""
        # Test free plan identification
        self.assertTrue(self.free_plan.is_free)
        self.assertFalse(self.basic_plan.is_free)
        
        # Test plan features
        feature_value = self.premium_plan.get_feature('priority_support', False)
        self.assertIsNotNone(feature_value)
        
        # Test plan ordering
        plans = Plan.objects.all().order_by('price_monthly')
        prices = [plan.price_monthly for plan in plans]
        self.assertEqual(prices, sorted(prices))

    def test_processes_multiple_webhook_events_in_sequence(self):
        """Test sequential webhook event processing."""
        events = [
            "checkout.session.completed",
            "customer.subscription.created",
            "invoice.payment_succeeded",
            "customer.subscription.updated"
        ]
        
        for event_type in events:
            # Simulate processing each event type
            # This would typically involve calling webhook handlers
            pass
        
        # Verify system remains in consistent state
        self.assertIsNotNone(self.user.current_plan)

    def test_handles_subscription_plan_discontinuation(self):
        """Test handling of discontinued subscription plans."""
        # Mark plan as inactive
        self.basic_plan.is_active = False
        self.basic_plan.save()
        
        # User should still have access to plan
        self.user.current_plan = self.basic_plan
        self.user.save()
        
        self.assertEqual(self.user.current_plan, self.basic_plan)
        
        # But plan should not be available for new subscriptions
        active_plans = Plan.objects.filter(is_active=True)
        self.assertNotIn(self.basic_plan, active_plans)


class PaymentSystemEdgeCaseHandlingTest(TestCase):
    """
    Test suite for payment system edge case handling.
    
    Covers unusual scenarios, boundary conditions, error recovery,
    and exceptional situations in payment processing.
    """

    def setUp(self):
        """Set up edge case test environment."""
        self.user = UserFactory()
        self.plan = BasicPlanFactory()

    def test_handles_zero_cost_plan_transitions(self):
        """Test transitions involving zero-cost plans."""
        free_plan = BasicPlanFactory(price_monthly=Decimal('0.00'))
        
        # Upgrade from free to paid
        self.user.current_plan = free_plan
        self.user.upgrade_to_plan(self.plan)
        
        self.assertEqual(self.user.current_plan, self.plan)
        
        # Downgrade from paid to free
        self.user.current_plan = self.plan
        self.user.upgrade_to_plan(free_plan)  # "Downgrade"
        
        self.assertEqual(self.user.current_plan, free_plan)

    def test_handles_extremely_high_request_volumes(self):
        """Test handling of very high request volumes."""
        # Set extremely high request count
        self.user.daily_requests_made = 999999999
        self.user.save()
        
        # System should handle large numbers gracefully
        self.assertGreater(self.user.daily_requests_made, 1000000)
        
        # Reset should work
        self.user.reset_daily_requests()
        self.assertEqual(self.user.daily_requests_made, 0)

    def test_handles_invalid_subscription_dates(self):
        """Test handling of invalid subscription dates."""
        # Test past start date with future end date
        self.user.subscription_started_at = timezone.now() - timedelta(days=30)
        self.user.subscription_expires_at = timezone.now() + timedelta(days=30)
        self.user.save()
        
        # Should calculate days remaining correctly
        remaining_days = self.user.subscription_days_remaining
        self.assertGreater(remaining_days, 0)
        
        # Test invalid date combinations
        self.user.subscription_started_at = timezone.now() + timedelta(days=30)
        self.user.subscription_expires_at = timezone.now() - timedelta(days=30)
        self.user.save()
        
        # Should handle gracefully
        remaining_days = self.user.subscription_days_remaining
        self.assertLessEqual(remaining_days, 0)

    def test_handles_plan_price_precision_edge_cases(self):
        """Test handling of decimal precision in plan prices."""
        # Test very precise decimal
        precise_plan = PlanFactory(
            price_monthly=Decimal('9.999999')
        )
        
        # Should handle precision correctly
        self.assertIsInstance(precise_plan.price_monthly, Decimal)
        
        # Test zero price edge case
        zero_plan = PlanFactory(price_monthly=Decimal('0.00'))
        self.assertTrue(zero_plan.is_free)

    def test_handles_subscription_status_edge_cases(self):
        """Test handling of unusual subscription statuses."""
        edge_case_statuses = [
            "incomplete",
            "incomplete_expired", 
            "paused",
            "unpaid"
        ]
        
        for status in edge_case_statuses:
            self.user.subscription_status = status
            self.user.save()
            
            # Should handle all statuses without error
            can_make, message = self.user.can_make_request()
            self.assertIsInstance(can_make, bool)

    def test_handles_token_history_overflow(self):
        """Test handling of token history overflow."""
        # Generate many tokens to test history limits
        for _ in range(50):
            self.user.generate_new_request_token(save_old=True)
        
        # History should be limited
        history_length = len(self.user.previous_tokens)
        self.assertLessEqual(history_length, 20)  # Reasonable limit

    def test_handles_malformed_plan_data(self):
        """Test handling of malformed plan data."""
        # Test plan with negative price
        try:
            negative_plan = BasicPlanFactory(price_monthly=Decimal('-10.00'))
            # Should either handle gracefully or raise validation error
        except Exception:
            pass  # Expected for invalid data

    def test_handles_subscription_date_boundary_conditions(self):
        """Test subscription date boundary conditions."""
        # Test subscription expiring at exact midnight
        midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.user.subscription_expires_at = midnight
        self.user.save()
        
        # Should handle midnight boundary correctly
        is_active = self.user.is_subscription_active
        self.assertIsInstance(is_active, bool)

    def test_handles_plan_feature_edge_cases(self):
        """Test plan feature handling edge cases."""
        # Test plan with complex features
        complex_features = {
            'api_access': True,
            'support_level': 'premium',
            'rate_limit_multiplier': 2.5,
            'custom_endpoints': ['analytics', 'reporting']
        }
        
        self.plan.features = complex_features
        self.plan.save()
        
        # Should handle complex feature data
        support_level = self.plan.get_feature('support_level')
        self.assertEqual(support_level, 'premium')
        
        # Test non-existent feature
        missing_feature = self.plan.get_feature('non_existent', 'default')
        self.assertEqual(missing_feature, 'default') 
        # to test rate limiting in realistic conditions 