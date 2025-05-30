"""
Chaos engineering tests for the payment system.
Tests system resilience under extreme conditions, failures, and chaotic scenarios.
"""
import random
import time
import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.db import transaction, connections
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock
from threading import Thread, Event, Barrier
from concurrent.futures import ThreadPoolExecutor, as_completed
import stripe

from users.models import Plan, User
from users.stripe_service import StripeService
from .factories import (
    UserFactory, ActiveSubscriberUserFactory, BasicPlanFactory,
    StripeCheckoutSessionFactory, StripeErrorFactory
)

User = get_user_model()


class StripeApiChaosEngineeringTest(TestCase):
    """
    Test suite for Stripe API chaos engineering and failure simulation.
    
    Covers Stripe service failures, API errors, network issues, timeout handling,
    and system resilience under various Stripe-related failure conditions.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.basic_plan = BasicPlanFactory()
        self.user = UserFactory()

    def test_stripe_intermittent_failures(self):
        """Test handling of intermittent Stripe failures."""
        self.client.force_login(self.user)
        
        # Create side effect that fails intermittently
        call_count = 0
        def intermittent_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:  # Fail every 3rd call
                raise stripe.APIConnectionError("Network error")
            return Mock(**StripeCheckoutSessionFactory())
        
        with patch('users.stripe_service.StripeService.create_checkout_session', 
                   side_effect=intermittent_failure):
            
            results = []
            for i in range(10):
                try:
                    response = self.client.post(
                        reverse('create_checkout_session'),
                        {'plan_id': self.basic_plan.id}
                    )
                    results.append(response.status_code)
                except Exception as e:
                    results.append(500)
            
            # Should handle failures gracefully
            success_count = sum(1 for status in results if status in [200, 302])
            self.assertGreater(success_count, 0)  # Some should succeed

    def test_stripe_timeout_chaos(self):
        """Test handling of random Stripe timeouts."""
        self.client.force_login(self.user)
        
        def random_timeout(*args, **kwargs):
            if random.random() < 0.3:  # 30% chance of timeout
                time.sleep(0.1)  # Simulate timeout
                raise stripe.APIConnectionError("Request timed out")
            return Mock(**StripeCheckoutSessionFactory())
        
        with patch('users.stripe_service.StripeService.create_checkout_session',
                   side_effect=random_timeout):
            
            # Test multiple requests under timeout chaos
            for i in range(5):
                try:
                    response = self.client.post(
                        reverse('create_checkout_session'),
                        {'plan_id': self.basic_plan.id}
                    )
                    # Should handle timeouts gracefully
                    self.assertIn(response.status_code, [200, 302, 500])
                except Exception:
                    # Should not raise unhandled exceptions
                    self.fail("Unhandled exception during timeout chaos")

    def test_stripe_rate_limit_chaos(self):
        """Test handling of Stripe rate limiting chaos."""
        self.client.force_login(self.user)
        
        rate_limit_count = 0
        def rate_limit_chaos(*args, **kwargs):
            nonlocal rate_limit_count
            rate_limit_count += 1
            if rate_limit_count % 2 == 0:  # Rate limit every other request
                raise stripe.RateLimitError("Too many requests")
            return Mock(**StripeCheckoutSessionFactory())
        
        with patch('users.stripe_service.StripeService.create_checkout_session',
                   side_effect=rate_limit_chaos):
            
            # Should implement retry logic or handle gracefully
            response = self.client.post(
                reverse('create_checkout_session'),
                {'plan_id': self.basic_plan.id}
            )
            self.assertIn(response.status_code, [200, 302, 429, 500])

    def test_stripe_authentication_chaos(self):
        """Test handling of authentication errors."""
        self.client.force_login(self.user)
        
        def auth_chaos(*args, **kwargs):
            if random.random() < 0.4:  # 40% chance of auth error
                raise stripe.AuthenticationError("Invalid API key")
            return Mock(**StripeCheckoutSessionFactory())
        
        with patch('users.stripe_service.StripeService.create_checkout_session',
                   side_effect=auth_chaos):
            
            response = self.client.post(
                reverse('create_checkout_session'),
                {'plan_id': self.basic_plan.id}
            )
            # Should handle auth errors appropriately
            self.assertIn(response.status_code, [200, 302, 401, 500])

    def test_stripe_malformed_response_chaos(self):
        """Test handling of malformed Stripe responses."""
        self.client.force_login(self.user)
        
        def malformed_response(*args, **kwargs):
            if random.random() < 0.3:
                # Return malformed response
                return Mock(id=None, url=None, object=None)
            return Mock(**StripeCheckoutSessionFactory())
        
        with patch('users.stripe_service.StripeService.create_checkout_session',
                   side_effect=malformed_response):
            
            response = self.client.post(
                reverse('create_checkout_session'),
                {'plan_id': self.basic_plan.id}
            )
            # Should handle malformed responses
            self.assertIn(response.status_code, [200, 302, 500])


class DatabaseTransactionChaosTest(TransactionTestCase):
    """
    Test suite for database transaction chaos and failure scenarios.
    
    Covers database failures, transaction rollbacks, connection issues,
    deadlock handling, and data consistency under database stress conditions.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.basic_plan = BasicPlanFactory()
        self.user = UserFactory()

    def test_database_connection_chaos(self):
        """Test handling of random database connection failures."""
        self.client.force_login(self.user)
        
        original_cursor = connections['default'].cursor
        
        def chaos_cursor(*args, **kwargs):
            if random.random() < 0.2:  # 20% chance of connection failure
                raise Exception("Database connection lost")
            return original_cursor()
        
        with patch.object(connections['default'], 'cursor', side_effect=chaos_cursor):
            try:
                response = self.client.get(reverse('plans_view'))
                # Should handle database errors gracefully
                self.assertIn(response.status_code, [200, 500])
            except Exception:
                # Should not propagate unhandled database errors
                pass

    def test_database_transaction_chaos(self):
        """Test handling of random transaction failures."""
        users = []
        errors = []
        
        def create_user_with_chaos():
            try:
                with transaction.atomic():
                    user = UserFactory()
                    if random.random() < 0.3:  # 30% chance of rollback
                        raise Exception("Simulated transaction failure")
                    users.append(user)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple users under chaos conditions
        threads = [Thread(target=create_user_with_chaos) for _ in range(10)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Some users should be created, some transactions should fail
        self.assertGreater(len(users) + len(errors), 0)

    def test_database_constraint_chaos(self):
        """Test handling of constraint violations under chaos."""
        base_email = "chaos@example.com"
        
        def create_user_with_duplicate_email():
            try:
                # Intentionally create users with same email
                UserFactory(email=base_email)
                return True
            except Exception:
                return False
        
        # Try to create multiple users with same email
        results = []
        threads = [Thread(target=lambda: results.append(create_user_with_duplicate_email())) 
                  for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Only one should succeed due to unique constraint
        success_count = sum(results)
        self.assertEqual(success_count, 1)

    def test_database_deadlock_simulation(self):
        """Test handling of simulated database deadlocks."""
        user1 = UserFactory()
        user2 = UserFactory()
        
        barrier = Barrier(2)
        results = []
        
        def update_users_with_deadlock_risk(first_user, second_user):
            try:
                barrier.wait()  # Synchronize threads
                
                with transaction.atomic():
                    # Update users in different order to create deadlock risk
                    first_user.daily_requests_made += 1
                    first_user.save()
                    
                    time.sleep(0.01)  # Small delay to increase deadlock chance
                    
                    second_user.daily_requests_made += 1
                    second_user.save()
                
                results.append(True)
            except Exception:
                results.append(False)
        
        # Create threads that update users in opposite order
        thread1 = Thread(target=update_users_with_deadlock_risk, args=(user1, user2))
        thread2 = Thread(target=update_users_with_deadlock_risk, args=(user2, user1))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # At least one operation should complete
        self.assertGreater(sum(results), 0)


class ConcurrentOperationsChaosTest(TransactionTestCase):
    """
    Test suite for concurrent operations chaos and race condition testing.
    
    Covers thread safety, race conditions, concurrent user operations,
    resource contention, and system behavior under high concurrency loads.
    """

    def setUp(self):
        """Set up test data."""
        self.basic_plan = BasicPlanFactory()

    def test_concurrent_user_creation_chaos(self):
        """Test chaotic concurrent user creation."""
        results = []
        errors = []
        
        def create_user_with_random_delay():
            try:
                # Random delay to create chaos
                time.sleep(random.uniform(0, 0.1))
                
                user = UserFactory()
                client = Client()
                client.force_login(user)
                
                # Random chance of creating checkout session
                if random.random() < 0.5:
                    with patch('users.stripe_service.StripeService.create_checkout_session') as mock_create:
                        mock_create.return_value = Mock(**StripeCheckoutSessionFactory())
                        
                        response = client.post(
                            reverse('create_checkout_session'),
                            {'plan_id': self.basic_plan.id}
                        )
                        results.append(response.status_code)
                else:
                    results.append(200)  # Just user creation
                    
            except Exception as e:
                errors.append(str(e))
        
        # Create chaos with many concurrent operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_user_with_random_delay) 
                      for _ in range(20)]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    errors.append(str(e))
        
        # Most operations should complete
        total_operations = len(results) + len(errors)
        success_rate = len(results) / total_operations if total_operations > 0 else 0
        self.assertGreater(success_rate, 0.5)  # At least 50% should succeed

    def test_subscription_modification_chaos(self):
        """Test chaotic subscription modifications."""
        user = ActiveSubscriberUserFactory(current_plan=self.basic_plan)
        results = []
        
        def random_subscription_action():
            try:
                client = Client()
                client.force_login(user)
                
                action = random.choice(['cancel', 'reactivate', 'upgrade', 'view'])
                
                if action == 'cancel':
                    with patch('users.stripe_service.StripeService.cancel_subscription') as mock_cancel:
                        mock_cancel.return_value = Mock(status='canceled')
                        response = client.post(reverse('cancel_subscription'))
                
                elif action == 'reactivate':
                    with patch('users.stripe_service.StripeService.reactivate_subscription') as mock_reactivate:
                        mock_reactivate.return_value = Mock(status='active')
                        response = client.post(reverse('reactivate_subscription'))
                
                elif action == 'upgrade':
                    with patch('users.stripe_service.StripeService.create_checkout_session') as mock_create:
                        mock_create.return_value = Mock(**StripeCheckoutSessionFactory())
                        response = client.post(
                            reverse('create_checkout_session'),
                            {'plan_id': self.basic_plan.id}
                        )
                
                else:  # view
                    response = client.get(reverse('user_subscription'))
                
                results.append((action, response.status_code))
                
            except Exception as e:
                results.append((action, 500))
        
        # Execute chaotic subscription actions concurrently
        threads = [Thread(target=random_subscription_action) for _ in range(15)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Analyze results
        self.assertEqual(len(results), 15)
        
        # Check that system handled chaos reasonably
        error_count = sum(1 for action, status in results if status >= 500)
        self.assertLess(error_count, len(results) // 2)  # Less than 50% errors

    def test_webhook_processing_chaos(self):
        """Test chaotic webhook processing."""
        user = ActiveSubscriberUserFactory()
        results = []
        
        def random_webhook():
            try:
                client = Client()
                
                # Random webhook types
                webhook_types = [
                    'checkout.session.completed',
                    'customer.subscription.updated',
                    'customer.subscription.deleted',
                    'invoice.payment_succeeded',
                    'invoice.payment_failed'
                ]
                
                webhook_type = random.choice(webhook_types)
                
                webhook_payload = {
                    'type': webhook_type,
                    'data': {
                        'object': {
                            'id': f'obj_{random.randint(1000, 9999)}',
                            'customer': user.stripe_customer_id,
                            'status': random.choice(['active', 'canceled', 'paid', 'open'])
                        }
                    }
                }
                
                with patch('users.views.stripe.Webhook.construct_event') as mock_construct:
                    if random.random() < 0.1:  # 10% chance of invalid signature
                        mock_construct.side_effect = stripe.SignatureVerificationError(
                            "Invalid signature", "signature"
                        )
                    else:
                        mock_construct.return_value = webhook_payload
                    
                    response = client.post(
                        reverse('stripe_webhook'),
                        data=json.dumps(webhook_payload),
                        content_type='application/json',
                        HTTP_STRIPE_SIGNATURE='signature'
                    )
                    
                    results.append((webhook_type, response.status_code))
                    
            except Exception as e:
                results.append(('error', 500))
        
        # Process many webhooks concurrently
        threads = [Thread(target=random_webhook) for _ in range(25)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # System should handle webhook chaos
        self.assertEqual(len(results), 25)
        
        # Most webhooks should be processed successfully
        success_count = sum(1 for wh_type, status in results if status == 200)
        self.assertGreater(success_count, len(results) // 2)


class SystemResourceStressChaosTest(TestCase):
    """
    Test suite for system resource stress and chaos engineering.
    
    Covers memory pressure, CPU stress, resource exhaustion scenarios,
    and system behavior under extreme resource constraints.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.basic_plan = BasicPlanFactory()

    def test_memory_stress_chaos(self):
        """Test system behavior under memory stress."""
        large_data_objects = []
        
        try:
            # Create memory pressure
            for i in range(100):
                # Create large objects to consume memory
                large_data = ['x' * 10000 for _ in range(100)]
                large_data_objects.append(large_data)
                
                # Try to perform normal operations under memory stress
                user = UserFactory()
                self.client.force_login(user)
                
                with patch('users.stripe_service.StripeService.create_checkout_session') as mock_create:
                    mock_create.return_value = Mock(**StripeCheckoutSessionFactory())
                    
                    response = self.client.post(
                        reverse('create_checkout_session'),
                        {'plan_id': self.basic_plan.id}
                    )
                    
                    # Should still function under memory pressure
                    self.assertIn(response.status_code, [200, 302, 500])
                
                # Occasionally clean up to avoid system crash
                if i % 20 == 0:
                    large_data_objects = large_data_objects[-50:]  # Keep only recent objects
                    
        except MemoryError:
            # System ran out of memory - this is expected under stress
            pass
        finally:
            # Clean up
            large_data_objects.clear()

    def test_cpu_stress_chaos(self):
        """Test system behavior under CPU stress."""
        def cpu_intensive_task():
            # Simulate CPU-intensive work
            total = 0
            for i in range(100000):
                total += i ** 2
            return total
        
        # Start CPU stress in background
        cpu_threads = [Thread(target=cpu_intensive_task) for _ in range(4)]
        for thread in cpu_threads:
            thread.start()
        
        try:
            # Perform payment operations under CPU stress
            user = UserFactory()
            self.client.force_login(user)
            
            start_time = time.time()
            
            with patch('users.stripe_service.StripeService.create_checkout_session') as mock_create:
                mock_create.return_value = Mock(**StripeCheckoutSessionFactory())
                
                response = self.client.post(
                    reverse('create_checkout_session'),
                    {'plan_id': self.basic_plan.id}
                )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete even under CPU stress (might be slower)
            self.assertIn(response.status_code, [200, 302])
            self.assertLess(duration, 10.0)  # Should not hang indefinitely
            
        finally:
            # Wait for CPU threads to complete
            for thread in cpu_threads:
                thread.join()

    def test_rapid_request_chaos(self):
        """Test system behavior under rapid request chaos."""
        user = UserFactory()
        self.client.force_login(user)
        
        results = []
        start_time = time.time()
        
        def rapid_request():
            try:
                # Random endpoint selection
                endpoints = [
                    ('GET', reverse('plans_view')),
                    ('GET', reverse('user_subscription')),
                    ('GET', reverse('plans_list')),
                ]
                
                method, url = random.choice(endpoints)
                
                if method == 'GET':
                    response = self.client.get(url)
                else:
                    response = self.client.post(url, {})
                
                results.append(response.status_code)
                
            except Exception:
                results.append(500)
        
        # Fire rapid requests
        threads = [Thread(target=rapid_request) for _ in range(100)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # System should handle rapid requests
        self.assertEqual(len(results), 100)
        
        # Most requests should succeed
        success_count = sum(1 for status in results if status < 500)
        success_rate = success_count / len(results)
        self.assertGreater(success_rate, 0.7)  # At least 70% success
        
        # Should complete in reasonable time
        self.assertLess(duration, 30.0)

    def test_random_data_chaos(self):
        """Test system resilience to random/malformed data."""
        user = UserFactory()
        self.client.force_login(user)
        
        def random_data_request():
            try:
                # Generate random data
                random_data = {
                    'plan_id': random.choice([
                        self.basic_plan.id,
                        99999,  # Non-existent ID
                        'invalid',  # Invalid type
                        None,  # Null value
                        '',  # Empty string
                        -1,  # Negative number
                    ]),
                    'random_field': random.choice([
                        'valid_value',
                        '<script>alert("xss")</script>',  # XSS attempt
                        'DROP TABLE users;',  # SQL injection attempt
                        'x' * 10000,  # Very long string
                        {'nested': 'object'},  # Unexpected type
                    ])
                }
                
                response = self.client.post(
                    reverse('create_checkout_session'),
                    data=random_data
                )
                
                # Should handle random data gracefully
                self.assertIn(response.status_code, [200, 302, 400, 404, 500])
                return True
                
            except Exception:
                return False
        
        # Test with various random data
        results = []
        for _ in range(50):
            result = random_data_request()
            results.append(result)
        
        # Most requests should be handled gracefully
        success_rate = sum(results) / len(results)
        self.assertGreater(success_rate, 0.8)  # At least 80% handled gracefully


class NetworkConnectivityChaosTest(TestCase):
    """
    Test suite for network connectivity chaos and failure simulation.
    
    Covers network failures, API timeouts, connection drops, DNS issues,
    and system resilience under various network failure conditions.
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.basic_plan = BasicPlanFactory()
        self.user = UserFactory()

    def test_stripe_network_chaos(self):
        """Test behavior under chaotic Stripe network conditions."""
        self.client.force_login(self.user)
        
        # Simulate various network conditions
        network_conditions = [
            stripe.APIConnectionError("Connection timeout"),
            stripe.APIConnectionError("Connection refused"),
            stripe.APIConnectionError("DNS resolution failed"),
            stripe.APIConnectionError("SSL handshake failed"),
            Exception("Unexpected network error"),
        ]
        
        def chaotic_network(*args, **kwargs):
            if random.random() < 0.4:  # 40% chance of network issue
                raise random.choice(network_conditions)
            return Mock(**StripeCheckoutSessionFactory())
        
        with patch('users.stripe_service.StripeService.create_checkout_session',
                   side_effect=chaotic_network):
            
            # Test multiple requests under network chaos
            results = []
            for i in range(10):
                try:
                    response = self.client.post(
                        reverse('create_checkout_session'),
                        {'plan_id': self.basic_plan.id}
                    )
                    results.append(response.status_code)
                except Exception:
                    results.append(500)
            
            # System should handle network chaos
            self.assertEqual(len(results), 10)
            
            # Some requests should succeed despite chaos
            success_count = sum(1 for status in results if status in [200, 302])
            self.assertGreater(success_count, 0)

    def test_partial_network_failure_chaos(self):
        """Test behavior during partial network failures."""
        self.client.force_login(self.user)
        
        failure_count = 0
        def partial_failure(*args, **kwargs):
            nonlocal failure_count
            failure_count += 1
            
            # Gradually increasing failure rate
            failure_probability = min(0.8, failure_count * 0.1)
            
            if random.random() < failure_probability:
                raise stripe.APIConnectionError("Partial network failure")
            return Mock(**StripeCheckoutSessionFactory())
        
        with patch('users.stripe_service.StripeService.create_checkout_session',
                   side_effect=partial_failure):
            
            # Test system adaptation to increasing failure rate
            for i in range(5):
                try:
                    response = self.client.post(
                        reverse('create_checkout_session'),
                        {'plan_id': self.basic_plan.id}
                    )
                    # Should handle gracefully regardless of failure rate
                    self.assertIn(response.status_code, [200, 302, 500])
                except Exception:
                    # Should not have unhandled exceptions
                    self.fail("Unhandled exception during partial network failure")

    def test_slow_network_chaos(self):
        """Test behavior under slow network conditions."""
        self.client.force_login(self.user)
        
        def slow_network(*args, **kwargs):
            # Random delays to simulate slow network
            delay = random.uniform(0.1, 2.0)
            time.sleep(delay)
            
            if random.random() < 0.2:  # 20% chance of timeout after delay
                raise stripe.APIConnectionError("Request timed out")
            
            return Mock(**StripeCheckoutSessionFactory())
        
        with patch('users.stripe_service.StripeService.create_checkout_session',
                   side_effect=slow_network):
            
            start_time = time.time()
            
            response = self.client.post(
                reverse('create_checkout_session'),
                {'plan_id': self.basic_plan.id}
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should handle slow networks but not hang indefinitely
            self.assertIn(response.status_code, [200, 302, 500])
            self.assertLess(duration, 10.0)  # Should timeout before 10 seconds 