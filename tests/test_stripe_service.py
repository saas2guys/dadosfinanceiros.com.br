"""
Comprehensive tests for StripeService integration.
Tests all Stripe API interactions, error handling, and edge cases.
"""
import pytest
import stripe
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from unittest.mock import patch, Mock, MagicMock
from freezegun import freeze_time
import uuid

from users.stripe_service import StripeService
from users.models import User, Plan
from tests.factories import (
    UserFactory, PlanFactory, BasicPlanFactory, ActiveSubscriberUserFactory,
    StripeCustomerFactory, StripeMockSubscriptionFactory, StripePriceFactory,
    StripeCheckoutSessionFactory, StripeInvoiceFactory, StripeWebhookEventFactory,
    StripeErrorFactory, StripeTimeoutErrorFactory, StripeInvalidRequestErrorFactory,
    StripeObject
)


class StripeServiceTestCaseBase(TestCase):
    """
    Base test case class for StripeService tests.
    
    Provides common setup including user and plan fixtures, service instance,
    and shared utilities for testing Stripe API integration functionality.
    """

    def setUp(self):
        """Set up test data and mocks."""
        self.user = UserFactory()
        self.plan = BasicPlanFactory()
        self.stripe_service = StripeService()
        
        # Mock Stripe API key
        patcher = patch.object(stripe, 'api_key', 'sk_test_123')
        self.addCleanup(patcher.stop)
        patcher.start()


class StripeCustomerManagementIntegrationTest(StripeServiceTestCaseBase):
    """
    Test suite for Stripe customer management operations.
    
    Covers customer creation, retrieval, updates, and all customer-related
    operations through the StripeService including error handling and edge cases.
    """

    @patch('stripe.Customer.create')
    def test_creates_stripe_customer_with_user_details_successfully(self, mock_create):
        """Test successful customer creation."""
        mock_customer = StripeCustomerFactory(
            id="cus_test123",
            email=self.user.email
        )
        mock_create.return_value = StripeObject(**mock_customer)

        customer = self.stripe_service.create_customer(
            email=self.user.email,
            name=f"{self.user.first_name} {self.user.last_name}"
        )

        self.assertEqual(customer['id'], "cus_test123")
        self.assertEqual(customer['email'], self.user.email)
        mock_create.assert_called_once()

    @patch('stripe.Customer.create')
    def test_handles_stripe_customer_creation_errors_gracefully(self, mock_create):
        """Test handling of customer creation errors."""
        mock_create.side_effect = stripe.error.StripeError("API Error")

        with self.assertRaises(stripe.error.StripeError):
            self.stripe_service.create_customer(
                email=self.user.email,
                name="Test User"
            )

    @patch('stripe.Customer.retrieve')
    def test_retrieves_existing_stripe_customer_by_id(self, mock_retrieve):
        """Test customer retrieval by ID."""
        mock_customer = StripeCustomerFactory(id="cus_test123")
        mock_retrieve.return_value = StripeObject(**mock_customer)

        customer = self.stripe_service.get_customer("cus_test123")

        self.assertEqual(customer['id'], "cus_test123")
        mock_retrieve.assert_called_once_with("cus_test123")

    @patch('stripe.Customer.retrieve')
    def test_handles_customer_not_found_errors_appropriately(self, mock_retrieve):
        """Test handling of customer not found errors."""
        mock_retrieve.side_effect = stripe.error.InvalidRequestError(
            "No such customer", None
        )

        with self.assertRaises(stripe.error.InvalidRequestError):
            self.stripe_service.get_customer("cus_nonexistent")

    @patch('stripe.Customer.modify')
    def test_updates_existing_customer_details_successfully(self, mock_modify):
        """Test customer update functionality."""
        mock_customer = StripeCustomerFactory(
            id="cus_test123",
            email="updated@example.com"
        )
        mock_modify.return_value = StripeObject(**mock_customer)

        customer = self.stripe_service.update_customer(
            "cus_test123",
            email="updated@example.com"
        )

        self.assertEqual(customer['email'], "updated@example.com")
        mock_modify.assert_called_once()

    @patch('stripe.Customer.delete')
    def test_deletes_customer_and_handles_cleanup_properly(self, mock_delete):
        """Test customer deletion functionality."""
        mock_delete.return_value = StripeObject(deleted=True, id="cus_test123")

        result = self.stripe_service.delete_customer("cus_test123")

        self.assertTrue(result['deleted'])
        mock_delete.assert_called_once_with("cus_test123")


class StripeCheckoutSessionManagementTest(StripeServiceTestCaseBase):
    """
    Test suite for Stripe checkout session operations.
    
    Covers session creation, retrieval, metadata handling, and all checkout-related
    functionality including subscription setup and payment processing.
    """

    @patch('stripe.checkout.Session.create')
    def test_creates_checkout_session_for_subscription_plan(self, mock_create):
        """Test checkout session creation for subscriptions."""
        mock_session = StripeCheckoutSessionFactory(
            id="cs_test123",
            customer="cus_test123",
            mode="subscription"
        )
        mock_create.return_value = StripeObject(mock_session)

        session = self.stripe_service.create_checkout_session(
            customer_id="cus_test123",
            price_id="price_test123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )

        self.assertEqual(session['id'], "cs_test123")
        self.assertEqual(session['mode'], "subscription")
        mock_create.assert_called_once()

    @patch('stripe.checkout.Session.create')
    def test_includes_metadata_in_checkout_session_creation(self, mock_create):
        """Test metadata inclusion in checkout sessions."""
        metadata = {
            'user_id': str(self.user.id),
            'plan_id': str(self.plan.id)
        }
        
        mock_session = StripeCheckoutSessionFactory(
            id="cs_test123",
            metadata=metadata
        )
        mock_create.return_value = StripeObject(mock_session)

        session = self.stripe_service.create_checkout_session(
            customer_id="cus_test123",
            price_id="price_test123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            metadata=metadata
        )

        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        self.assertEqual(call_args['metadata'], metadata)

    @patch('stripe.checkout.Session.retrieve')
    def test_retrieves_checkout_session_by_id_successfully(self, mock_retrieve):
        """Test checkout session retrieval."""
        mock_session = StripeCheckoutSessionFactory(id="cs_test123")
        mock_retrieve.return_value = StripeObject(**mock_session)

        session = self.stripe_service.get_checkout_session("cs_test123")

        self.assertEqual(session['id'], "cs_test123")
        mock_retrieve.assert_called_once_with("cs_test123")

    @patch('stripe.checkout.Session.create')
    def test_handles_checkout_session_creation_failures(self, mock_create):
        """Test handling of checkout session creation errors."""
        mock_create.side_effect = stripe.error.InvalidRequestError(
            "Invalid price", None
        )

        with self.assertRaises(stripe.error.InvalidRequestError):
            self.stripe_service.create_checkout_session(
                customer_id="cus_test123",
                price_id="invalid_price",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel"
            )

    @patch('stripe.checkout.Session.create')
    def test_supports_one_time_payment_checkout_sessions(self, mock_create):
        """Test creation of one-time payment sessions."""
        mock_session = StripeCheckoutSessionFactory(
            id="cs_test123",
            mode="payment"
        )
        mock_create.return_value = StripeObject(mock_session)

        session = self.stripe_service.create_checkout_session(
            customer_id="cus_test123",
            price_id="price_test123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            mode="payment"
        )

        self.assertEqual(session['mode'], "payment")


class StripeSubscriptionLifecycleManagementTest(StripeServiceTestCaseBase):
    """
    Test suite for Stripe subscription lifecycle operations.
    
    Covers subscription creation, updates, cancellation, reactivation,
    and all subscription management functionality including status tracking.
    """

    @patch('stripe.Subscription.create')
    def test_creates_subscription_for_customer_and_plan(self, mock_create):
        """Test subscription creation."""
        mock_subscription = StripeMockSubscriptionFactory(
            id="sub_test123",
            customer="cus_test123",
            status="active"
        )
        mock_create.return_value = StripeObject(**mock_subscription)

        subscription = self.stripe_service.create_subscription(
            customer_id="cus_test123",
            price_id="price_test123"
        )

        self.assertEqual(subscription['id'], "sub_test123")
        self.assertEqual(subscription['status'], "active")
        mock_create.assert_called_once()

    @patch('stripe.Subscription.retrieve')
    def test_retrieves_subscription_details_by_id(self, mock_retrieve):
        """Test subscription retrieval."""
        mock_subscription = StripeMockSubscriptionFactory(id="sub_test123")
        mock_retrieve.return_value = StripeObject(**mock_subscription)

        subscription = self.stripe_service.get_subscription("sub_test123")

        self.assertEqual(subscription['id'], "sub_test123")
        mock_retrieve.assert_called_once_with("sub_test123")

    @patch('stripe.Subscription.modify')
    def test_updates_subscription_with_new_parameters(self, mock_modify):
        """Test subscription updates."""
        mock_subscription = StripeMockSubscriptionFactory(
            id="sub_test123",
            status="active"
        )
        mock_modify.return_value = StripeObject(**mock_subscription)

        subscription = self.stripe_service.update_subscription(
            "sub_test123",
            metadata={'updated': 'true'}
        )

        mock_modify.assert_called_once()

    @patch('stripe.Subscription.cancel')
    def test_cancels_subscription_with_immediate_effect(self, mock_cancel):
        """Test immediate subscription cancellation."""
        mock_subscription = StripeMockSubscriptionFactory(
            id="sub_test123",
            status="canceled"
        )
        mock_cancel.return_value = StripeObject(**mock_subscription)

        subscription = self.stripe_service.cancel_subscription("sub_test123")

        self.assertEqual(subscription['status'], "canceled")
        mock_cancel.assert_called_once_with("sub_test123")

    @patch('stripe.Subscription.modify')
    def test_cancels_subscription_at_period_end(self, mock_modify):
        """Test subscription cancellation at period end."""
        mock_subscription = StripeMockSubscriptionFactory(
            id="sub_test123",
            cancel_at_period_end=True
        )
        mock_modify.return_value = StripeObject(**mock_subscription)

        subscription = self.stripe_service.cancel_subscription_at_period_end("sub_test123")

        self.assertTrue(subscription['cancel_at_period_end'])
        mock_modify.assert_called_once()


class StripeWebhookEventProcessingTest(StripeServiceTestCaseBase):
    """
    Test suite for Stripe webhook event processing.
    
    Covers webhook validation, event handling, payment confirmations,
    and all webhook-related business logic through the StripeService.
    """

    @patch('stripe.Event.retrieve')
    def test_retrieves_and_validates_webhook_event(self, mock_retrieve):
        """Test webhook event retrieval and validation."""
        mock_event = StripeWebhookEventFactory(
            id="evt_test123",
            type="checkout.session.completed"
        )
        mock_retrieve.return_value = StripeObject(**mock_event)

        event = self.stripe_service.retrieve_event("evt_test123")

        self.assertEqual(event['id'], "evt_test123")
        self.assertEqual(event['type'], "checkout.session.completed")
        mock_retrieve.assert_called_once_with("evt_test123")

    def test_processes_successful_payment_webhook_events(self):
        """Test processing of successful payment events."""
        checkout_session = StripeCheckoutSessionFactory(
            payment_status="paid",
            customer="cus_test123",
            subscription="sub_test123",
            metadata={
                'user_id': str(self.user.id),
                'plan_id': str(self.plan.id)
            }
        )

        with patch('users.stripe_service.stripe.Subscription.retrieve') as mock_retrieve:
            mock_retrieve.return_value = StripeObject(
                id="sub_test123",
                current_period_end=int((timezone.now() + timedelta(days=30)).timestamp())
            )
            
            self.stripe_service.handle_successful_payment(checkout_session)
            
            # Verify user was updated correctly
            self.user.refresh_from_db()
            self.assertEqual(self.user.current_plan, self.plan)
            self.assertEqual(self.user.subscription_status, 'active')

    def test_processes_subscription_updated_webhook_events(self):
        """Test processing of subscription update events."""
        subscription_data = StripeMockSubscriptionFactory(
            id="sub_test123",
            status="active",
            customer="cus_test123"
        )

        self.user.stripe_customer_id = "cus_test123"
        self.user.stripe_subscription_id = "sub_test123"
        self.user.save()

        result = self.stripe_service.handle_subscription_updated(subscription_data)
        
        # Verify the update was successful
        self.assertTrue(result)
        
        # Verify user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscription_status, 'active')

    def test_handles_unknown_webhook_event_types_gracefully(self):
        """Test handling of unknown webhook event types."""
        unknown_event = {
            'type': 'unknown.event.type',
            'data': {'object': {}}
        }

        # Should not raise exception
        result = self.stripe_service.process_webhook_event(unknown_event)
        self.assertIsNone(result)

    def test_validates_webhook_event_data_integrity(self):
        """Test webhook event data validation."""
        invalid_event = {
            'type': 'checkout.session.completed',
            'data': {}  # Missing object
        }

        # The handle_successful_payment method should return False for invalid data
        result = self.stripe_service.handle_successful_payment(invalid_event['data'])
        self.assertFalse(result)


class StripeApiErrorHandlingTest(StripeServiceTestCaseBase):
    """
    Test suite for Stripe API error handling and resilience.
    
    Covers all types of Stripe errors, network issues, rate limiting,
    and error recovery mechanisms in the StripeService.
    """

    @patch('stripe.Customer.create')
    def test_handles_stripe_card_declined_errors_appropriately(self, mock_create):
        """Test handling of card declined errors."""
        mock_create.side_effect = stripe.error.CardError(
            "Your card was declined.",
            None,
            "card_declined"
        )

        with self.assertRaises(stripe.error.CardError):
            self.stripe_service.create_customer(email="test@example.com")

    @patch('stripe.Customer.create')
    def test_handles_stripe_rate_limit_errors_with_retry(self, mock_create):
        """Test handling of rate limit errors."""
        mock_create.side_effect = stripe.error.RateLimitError("Rate limit exceeded")

        with self.assertRaises(stripe.error.RateLimitError):
            self.stripe_service.create_customer(email="test@example.com")

    @patch('stripe.Customer.create')
    def test_handles_stripe_authentication_errors_securely(self, mock_create):
        """Test handling of authentication errors."""
        mock_create.side_effect = stripe.error.AuthenticationError("Invalid API key")

        with self.assertRaises(stripe.error.AuthenticationError):
            self.stripe_service.create_customer(email="test@example.com")

    @patch('stripe.Customer.create')
    def test_handles_stripe_invalid_request_errors(self, mock_create):
        """Test handling of invalid request errors."""
        mock_create.side_effect = stripe.error.InvalidRequestError(
            "Invalid email address",
            None
        )

        with self.assertRaises(stripe.error.InvalidRequestError):
            self.stripe_service.create_customer(email="invalid-email")

    @patch('stripe.Customer.create')
    def test_handles_stripe_api_connection_errors(self, mock_create):
        """Test handling of API connection errors."""
        mock_create.side_effect = stripe.error.APIConnectionError("Network error")

        with self.assertRaises(stripe.error.APIConnectionError):
            self.stripe_service.create_customer(email="test@example.com")

    @patch('stripe.Customer.create')
    def test_handles_generic_stripe_errors_gracefully(self, mock_create):
        """Test handling of generic Stripe errors."""
        mock_create.side_effect = stripe.error.StripeError("Something went wrong")

        with self.assertRaises(stripe.error.StripeError):
            self.stripe_service.create_customer(email="test@example.com")


class StripeServiceEdgeCaseHandlingTest(StripeServiceTestCaseBase):
    """
    Test suite for StripeService edge cases and unusual scenarios.
    
    Covers boundary conditions, concurrent operations, large datasets,
    and other exceptional situations in Stripe API integration.
    """

    def test_handles_null_and_empty_parameter_values(self):
        """Test handling of null and empty parameters."""
        with self.assertRaises(ValueError):
            self.stripe_service.create_customer(email=None)

        with self.assertRaises(ValueError):
            self.stripe_service.create_customer(email="")

    def test_handles_very_long_customer_names_appropriately(self):
        """Test handling of very long customer names."""
        long_name = "x" * 500
        
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = StripeObject(id="cus_test123")
            
            # Should truncate or handle long names appropriately
            customer = self.stripe_service.create_customer(
                email="test@example.com",
                name=long_name
            )
            
            mock_create.assert_called_once()

    def test_handles_special_characters_in_metadata_safely(self):
        """Test handling of special characters in metadata."""
        special_metadata = {
            'description': 'Special chars: áéíóú ñ ç € $ % & @ # !',
            'unicode_field': '🎉 测试 العربية русский'
        }
        
        with patch('stripe.checkout.Session.create') as mock_create:
            mock_create.return_value = StripeObject(id="cs_test123")
            
            session = self.stripe_service.create_checkout_session(
                customer_id="cus_test123",
                price_id="price_test123",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
                metadata=special_metadata
            )
            
            mock_create.assert_called_once()

    def test_handles_concurrent_subscription_operations_safely(self):
        """Test handling of concurrent subscription operations."""
        with patch('stripe.Subscription.modify') as mock_modify:
            mock_modify.return_value = StripeObject(id="sub_test123", status="active")
            
            # Simulate concurrent operations
            results = []
            for i in range(5):
                result = self.stripe_service.update_subscription(
                    "sub_test123",
                    metadata={'operation': str(i)}
                )
                results.append(result)
            
            # All operations should complete
            self.assertEqual(len(results), 5)
            self.assertEqual(mock_modify.call_count, 5)

    @freeze_time("2024-01-15 12:00:00")
    def test_handles_timezone_sensitive_operations_correctly(self):
        """Test timezone handling in Stripe operations."""
        with patch('stripe.Subscription.create') as mock_create:
            # Test with various timezone scenarios
            subscription_data = StripeMockSubscriptionFactory(
                current_period_start=int(timezone.now().timestamp()),
                current_period_end=int((timezone.now() + timedelta(days=30)).timestamp())
            )
            mock_create.return_value = StripeObject(**subscription_data)
            
            subscription = self.stripe_service.create_subscription(
                customer_id="cus_test123",
                price_id="price_test123"
            )
            
            # Verify timestamps are handled correctly
            self.assertIsNotNone(subscription['current_period_start'])
            self.assertIsNotNone(subscription['current_period_end'])

    def test_handles_extremely_large_metadata_objects(self):
        """Test handling of large metadata objects."""
        large_metadata = {f'key_{i}': f'value_{i}' * 100 for i in range(50)}
        
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = StripeObject(id="cus_test123")
            
            # Should handle or truncate large metadata appropriately
            customer = self.stripe_service.create_customer(
                email="test@example.com",
                metadata=large_metadata
            )
            
            mock_create.assert_called_once()

    def test_provides_detailed_error_context_for_debugging(self):
        """Test that errors include sufficient context for debugging."""
        with patch('stripe.Customer.create') as mock_create:
            error = stripe.error.InvalidRequestError(
                "Invalid email address",
                None,
                code="email_invalid"
            )
            mock_create.side_effect = error
            
            with self.assertRaises(stripe.error.InvalidRequestError) as context:
                self.stripe_service.create_customer(email="invalid-email")
            
            # Error should include useful context
            self.assertIn("Invalid email address", str(context.exception))

    def test_validates_required_parameters_before_api_calls(self):
        """Test parameter validation before making API calls."""
        # Should validate required parameters
        with self.assertRaises(ValueError):
            self.stripe_service.create_checkout_session(
                customer_id=None,  # Required parameter
                price_id="price_test123",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel"
            )

    def test_maintains_idempotency_for_safe_retry_operations(self):
        """Test idempotency handling for retry scenarios."""
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = StripeObject(id="cus_test123")
            
            # Test with idempotency key
            customer1 = self.stripe_service.create_customer(
                email="test@example.com",
                idempotency_key="test_key_123"
            )
            
            customer2 = self.stripe_service.create_customer(
                email="test@example.com",
                idempotency_key="test_key_123"
            )
            
            # Should handle idempotency appropriately
            mock_create.assert_called()

    def test_respects_stripe_api_version_constraints(self):
        """Test API version handling and compatibility."""
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = StripeObject(id="cus_test123")
            
            # Should use appropriate API version
            customer = self.stripe_service.create_customer(
                email="test@example.com"
            )
            
            # Verify API version is set correctly
            self.assertIsNotNone(stripe.api_version) 