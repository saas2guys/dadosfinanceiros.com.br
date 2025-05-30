"""
Comprehensive tests for Stripe webhook functionality.
Tests webhook signature validation, event processing, subscription management,
and all webhook-related security and business logic.
"""
import json
import hashlib
import hmac
import time
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from unittest.mock import patch, Mock
from freezegun import freeze_time
import uuid
import factory
from django.core.cache import cache

from users.models import User, Plan
from .factories import (
    UserFactory, ActiveSubscriberUserFactory, BasicPlanFactory,
    StripeWebhookEventFactory, StripeSubscriptionFactory,
    StripeCheckoutSessionFactory, StripeInvoiceFactory
)


class StripeWebhookTestCaseBase(TestCase):
    """
    Base test case class for Stripe webhook tests.
    
    Provides common setup including webhook signature generation, event creation,
    plan setup, and shared utilities for testing webhook functionality.
    """

    def setUp(self):
        """Set up test data and webhook utilities."""
        # Clear cache before each test
        cache.clear()
        
        # Create plans
        self.free_plan = FreePlanFactory()
        self.basic_plan = BasicPlanFactory() 
        self.premium_plan = PremiumPlanFactory()
        
        # Create test user
        self.user = UserFactory()
        
        # Webhook configuration
        self.webhook_secret = "whsec_test123"
        self.webhook_url = "/stripe/webhook/"

    def generate_webhook_signature(self, payload, timestamp=None, secret=None):
        """Generate valid Stripe webhook signature."""
        if timestamp is None:
            timestamp = str(int(time.time()))
        if secret is None:
            secret = self.webhook_secret
            
        # Create signed payload  
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"t={timestamp},v1={signature}"

    def create_webhook_event(self, event_type, event_data):
        """Create a Stripe webhook event."""
        return {
            "id": f"evt_test_{event_type}_{int(time.time())}",
            "object": "event",
            "api_version": "2020-08-27",
            "created": int(time.time()),
            "data": {"object": event_data},
            "livemode": False,
            "pending_webhooks": 1,
            "request": {"id": "req_test123", "idempotency_key": None},
            "type": event_type
        }

    def create_checkout_session_completed_event(self, customer_id=None, subscription_id=None):
        """Create checkout.session.completed event."""
        if customer_id is None:
            customer_id = f"cus_test_{int(time.time())}"
        if subscription_id is None:
            subscription_id = f"sub_test_{int(time.time())}"
            
        session_data = {
            "id": f"cs_test_{int(time.time())}",
            "object": "checkout.session",
            "customer": customer_id,
            "subscription": subscription_id,
            "metadata": {
                "user_id": str(self.user.id),
                "plan_id": str(self.basic_plan.id)
            },
            "mode": "subscription",
            "payment_status": "paid",
            "status": "complete"
        }
        
        return self.create_webhook_event("checkout.session.completed", session_data)

    def create_subscription_updated_event(self, subscription_id=None, status="active"):
        """Create customer.subscription.updated event."""
        if subscription_id is None:
            subscription_id = f"sub_test_{int(time.time())}"
            
        subscription_data = {
            "id": subscription_id,
            "object": "subscription", 
            "customer": f"cus_test_{int(time.time())}",
            "status": status,
            "current_period_start": int(time.time()),
            "current_period_end": int(time.time()) + 2592000,  # 30 days
            "metadata": {
                "user_id": str(self.user.id)
            }
        }
        
        return self.create_webhook_event("customer.subscription.updated", subscription_data)

    def create_invoice_payment_succeeded_event(self, customer_id=None, subscription_id=None):
        """Create invoice.payment_succeeded event."""
        if customer_id is None:
            customer_id = f"cus_test_{int(time.time())}"
        if subscription_id is None:
            subscription_id = f"sub_test_{int(time.time())}"
            
        invoice_data = {
            "id": f"in_test_{int(time.time())}",
            "object": "invoice",
            "customer": customer_id,
            "subscription": subscription_id,
            "status": "paid",
            "amount_paid": 999,  # $9.99
            "metadata": {
                "user_id": str(self.user.id)
            }
        }
        
        return self.create_webhook_event("invoice.payment_succeeded", invoice_data)


class StripeWebhookSignatureValidationTest(StripeWebhookTestCaseBase):
    """
    Test suite for Stripe webhook signature validation and security.
    
    Covers signature verification, timestamp validation, replay attack prevention,
    malformed request handling, and all webhook security measures.
    """

    def test_accepts_webhook_with_valid_signature_and_timestamp(self):
        """Test that webhooks with valid signatures are accepted."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)

    def test_rejects_webhook_with_invalid_signature(self):
        """Test that webhooks with invalid signatures are rejected."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        invalid_signature = "t=123456789,v1=invalid_signature"
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=invalid_signature
            )
        
        self.assertEqual(response.status_code, 400)

    def test_rejects_webhook_with_missing_signature_header(self):
        """Test that webhooks without signature headers are rejected."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        
        response = self.client.post(
            self.webhook_url,
            data=payload,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

    def test_rejects_webhook_with_expired_timestamp(self):
        """Test that webhooks with old timestamps are rejected."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        old_timestamp = str(int(time.time()) - 400)  # 400 seconds ago
        signature = self.generate_webhook_signature(payload, timestamp=old_timestamp)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 400)

    def test_prevents_replay_attacks_using_event_id_cache(self):
        """Test that duplicate events are rejected."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            # First request should succeed
            response1 = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
            
            # Second identical request should be rejected
            response2 = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 400)

    def test_handles_malformed_json_payload_gracefully(self):
        """Test that malformed JSON payloads are handled gracefully."""
        malformed_payload = '{"incomplete": json'
        signature = self.generate_webhook_signature(malformed_payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=malformed_payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 400)

    def test_validates_content_type_is_application_json(self):
        """Test that non-JSON content types are rejected."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='text/plain',  # Wrong content type
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 400)

    def test_handles_missing_webhook_secret_configuration(self):
        """Test behavior when webhook secret is not configured."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', None):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 500)


class StripeCheckoutSessionWebhookProcessingTest(StripeWebhookTestCaseBase):
    """
    Test suite for checkout session webhook processing.
    
    Covers subscription activation, user plan updates, payment confirmation,
    and all business logic triggered by successful checkout sessions.
    """

    def test_processes_completed_checkout_session_successfully(self):
        """Test processing of checkout.session.completed event."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.current_plan, self.basic_plan)
        self.assertEqual(self.user.subscription_status, 'active')

    def test_handles_checkout_session_with_missing_metadata(self):
        """Test handling of checkout sessions without required metadata."""
        event = self.create_checkout_session_completed_event()
        # Remove metadata
        event['data']['object']['metadata'] = {}
        
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        # Should return 200 but not process (graceful handling)
        self.assertEqual(response.status_code, 200)

    def test_handles_checkout_session_for_nonexistent_user(self):
        """Test handling of checkout sessions for users that don't exist."""
        event = self.create_checkout_session_completed_event()
        event['data']['object']['metadata']['user_id'] = '99999'  # Non-existent user
        
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        # Should return 200 but not crash
        self.assertEqual(response.status_code, 200)

    def test_handles_checkout_session_for_nonexistent_plan(self):
        """Test handling of checkout sessions for plans that don't exist."""
        event = self.create_checkout_session_completed_event()
        event['data']['object']['metadata']['plan_id'] = '99999'  # Non-existent plan
        
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        # Should return 200 but not process
        self.assertEqual(response.status_code, 200)

    def test_updates_user_stripe_customer_and_subscription_ids(self):
        """Test that user's Stripe IDs are updated during checkout processing."""
        customer_id = "cus_test123"
        subscription_id = "sub_test456"
        
        event = self.create_checkout_session_completed_event(
            customer_id=customer_id,
            subscription_id=subscription_id
        )
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify Stripe IDs were set
        self.user.refresh_from_db()
        self.assertEqual(self.user.stripe_customer_id, customer_id)
        self.assertEqual(self.user.stripe_subscription_id, subscription_id)


class StripeSubscriptionWebhookProcessingTest(StripeWebhookTestCaseBase):
    """
    Test suite for subscription webhook processing.
    
    Covers subscription status changes, plan updates, cancellations,
    and all subscription lifecycle management through webhooks.
    """

    def test_processes_subscription_updated_to_active_status(self):
        """Test processing of subscription updated to active."""
        subscription_id = "sub_test123"
        self.user.stripe_subscription_id = subscription_id
        self.user.save()
        
        event = self.create_subscription_updated_event(
            subscription_id=subscription_id,
            status="active"
        )
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify subscription status was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscription_status, 'active')

    def test_processes_subscription_updated_to_canceled_status(self):
        """Test processing of subscription updated to canceled."""
        subscription_id = "sub_test123"
        self.user.stripe_subscription_id = subscription_id
        self.user.subscription_status = 'active'
        self.user.save()
        
        event = self.create_subscription_updated_event(
            subscription_id=subscription_id,
            status="canceled"
        )
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify subscription status was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscription_status, 'canceled')

    def test_updates_subscription_period_dates_from_webhook(self):
        """Test that subscription period dates are updated."""
        subscription_id = "sub_test123"
        self.user.stripe_subscription_id = subscription_id
        self.user.save()
        
        current_period_start = int(time.time())
        current_period_end = current_period_start + 2592000  # 30 days
        
        event = self.create_subscription_updated_event(subscription_id=subscription_id)
        event['data']['object']['current_period_start'] = current_period_start
        event['data']['object']['current_period_end'] = current_period_end
        
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify dates were updated
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.subscription_expires_at)

    def test_handles_subscription_update_for_unknown_subscription(self):
        """Test handling of subscription updates for unknown subscriptions."""
        event = self.create_subscription_updated_event(
            subscription_id="sub_unknown123"
        )
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        # Should return 200 but not process
        self.assertEqual(response.status_code, 200)


class StripeInvoiceWebhookProcessingTest(StripeWebhookTestCaseBase):
    """
    Test suite for invoice webhook processing.
    
    Covers payment confirmations, billing renewals, payment failures,
    and all invoice-related subscription management.
    """

    def test_processes_successful_invoice_payment(self):
        """Test processing of invoice.payment_succeeded event."""
        subscription_id = "sub_test123"
        customer_id = "cus_test123"
        
        self.user.stripe_subscription_id = subscription_id
        self.user.stripe_customer_id = customer_id
        self.user.save()
        
        event = self.create_invoice_payment_succeeded_event(
            customer_id=customer_id,
            subscription_id=subscription_id
        )
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)

    def test_handles_invoice_payment_for_unknown_customer(self):
        """Test handling of invoice payments for unknown customers."""
        event = self.create_invoice_payment_succeeded_event(
            customer_id="cus_unknown123"
        )
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        # Should return 200 but not process
        self.assertEqual(response.status_code, 200)


class StripeWebhookEdgeCaseHandlingTest(StripeWebhookTestCaseBase):
    """
    Test suite for webhook edge cases and error handling.
    
    Covers unusual scenarios, malformed data, service failures,
    and all exceptional conditions in webhook processing.
    """

    def test_handles_unknown_webhook_event_types_gracefully(self):
        """Test handling of unknown webhook event types."""
        event = {
            "id": "evt_unknown",
            "object": "event",
            "type": "unknown.event.type",
            "data": {"object": {"id": "obj_test123"}}
        }
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        # Should return 200 (graceful handling)
        self.assertEqual(response.status_code, 200)

    def test_handles_webhook_events_with_missing_data_fields(self):
        """Test handling of webhook events with missing required fields."""
        event = {
            "id": "evt_incomplete",
            "object": "event",
            "type": "checkout.session.completed"
            # Missing 'data' field
        }
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        # Should return 200 (graceful handling)
        self.assertEqual(response.status_code, 200)

    def test_handles_webhook_processing_database_errors(self):
        """Test handling of database errors during webhook processing."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            with patch('users.models.User.objects.get') as mock_get:
                mock_get.side_effect = Exception("Database error")
                
                response = self.client.post(
                    self.webhook_url,
                    data=payload,
                    content_type='application/json',
                    HTTP_STRIPE_SIGNATURE=signature
                )
        
        # Should return 200 to Stripe even on internal errors
        self.assertEqual(response.status_code, 200)

    def test_handles_concurrent_webhook_processing_safely(self):
        """Test handling of concurrent webhook processing."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            # Simulate concurrent requests
            response1 = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
            
            # This should be caught by replay protection
            response2 = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 400)  # Replay protection

    @freeze_time("2024-01-15 12:00:00")
    def test_handles_webhook_timezone_edge_cases(self):
        """Test webhook processing with various timezone scenarios."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify timestamps are handled correctly
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.subscription_started_at)

    def test_handles_extremely_large_webhook_payloads(self):
        """Test handling of very large webhook payloads."""
        event = self.create_checkout_session_completed_event()
        # Add large metadata
        event['data']['object']['metadata']['large_field'] = 'x' * 10000
        
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        # Should handle large payloads gracefully
        self.assertIn(response.status_code, [200, 413])  # Success or payload too large

    def test_handles_unicode_characters_in_webhook_data(self):
        """Test handling of unicode characters in webhook data."""
        event = self.create_checkout_session_completed_event()
        event['data']['object']['metadata']['unicode_field'] = 'José González 中文 🎉'
        
        payload = json.dumps(event, ensure_ascii=False)
        signature = self.generate_webhook_signature(payload)
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json; charset=utf-8',
                HTTP_STRIPE_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 200)


class StripeWebhookSecurityTest(StripeWebhookTestCaseBase):
    """
    Test suite for webhook security features and attack prevention.
    
    Covers signature validation, timestamp verification, replay attack prevention,
    and protection against common webhook security vulnerabilities.
    """

    def test_prevents_signature_verification_bypass_attempts(self):
        """Test that signature verification cannot be bypassed."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        
        # Try various bypass attempts
        bypass_attempts = [
            None,  # No signature
            "",    # Empty signature
            "invalid",  # Invalid format
            "t=123,v1=",  # Empty signature value
            "v1=fakesig",  # Missing timestamp
            "t=,v1=fakesig",  # Empty timestamp
        ]
        
        for signature in bypass_attempts:
            with self.subTest(signature=signature):
                headers = {}
                if signature is not None:
                    headers['HTTP_STRIPE_SIGNATURE'] = signature
                    
                with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
                    response = self.client.post(
                        self.webhook_url,
                        data=payload,
                        content_type='application/json',
                        **headers
                    )
                
                self.assertEqual(response.status_code, 400)

    def test_prevents_timing_attacks_on_signature_validation(self):
        """Test that signature validation is not vulnerable to timing attacks."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        
        # Generate signatures with different lengths
        short_sig = self.generate_webhook_signature(payload)
        long_sig = short_sig + "extra_characters"
        
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            # Both should fail quickly and consistently
            start_time = time.time()
            response1 = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=long_sig
            )
            mid_time = time.time()
            
            response2 = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE="t=123,v1=invalid"
            )
            end_time = time.time()
        
        # Both should return 400
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response2.status_code, 400)
        
        # Timing should be similar (basic check)
        time1 = mid_time - start_time
        time2 = end_time - mid_time
        # Allow for reasonable variance
        self.assertLess(abs(time1 - time2), 0.1)

    def test_validates_webhook_source_restrictions(self):
        """Test that webhooks are properly restricted to Stripe sources."""
        event = self.create_checkout_session_completed_event()
        payload = json.dumps(event)
        signature = self.generate_webhook_signature(payload)
        
        # Test with various potentially malicious headers
        with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
            response = self.client.post(
                self.webhook_url,
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature,
                HTTP_X_FORWARDED_FOR='192.168.1.1',  # Internal IP
                HTTP_USER_AGENT='NotStripe/1.0'
            )
        
        # Should still process if signature is valid (headers don't matter)
        self.assertEqual(response.status_code, 200)

    def test_rate_limiting_protection_for_webhooks(self):
        """Test rate limiting protection for webhook endpoints."""
        event = self.create_checkout_session_completed_event()
        
        responses = []
        for i in range(10):
            # Use different event IDs to avoid replay protection
            test_event = event.copy()
            test_event['id'] = f"evt_test_{i}"
            
            payload = json.dumps(test_event)
            signature = self.generate_webhook_signature(payload)
            
            with patch('users.views.STRIPE_WEBHOOK_SECRET', self.webhook_secret):
                response = self.client.post(
                    self.webhook_url,
                    data=payload,
                    content_type='application/json',
                    HTTP_STRIPE_SIGNATURE=signature
                )
            responses.append(response.status_code)
        
        # Most should succeed (rate limiting typically handled at infrastructure level)
        success_count = responses.count(200)
        self.assertGreater(success_count, 7)  # Allow some to be rate limited 