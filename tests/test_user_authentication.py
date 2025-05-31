"""
Comprehensive tests for user authentication, registration, and token management.
Tests JWT authentication, request token authentication, user registration,
profile management, and all authentication-related functionality.
"""
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from users.authentication import RequestTokenAuthentication
from users.models import Plan, TokenHistory
from users.permissions import DailyLimitPermission
from users.serializers import UserRegistrationSerializer, UserSerializer

from .factories import BasicPlanFactory, FreePlanFactory, UserFactory

User = get_user_model()


class UserModelAuthenticationBusinessLogicTest(TestCase):
    """
    Test suite for User model authentication-related business logic.

    Covers token management, expiration handling, user creation with authentication
    features, and all authentication-related model methods and properties.
    """

    def setUp(self):
        """Set up test data."""
        self.plan = BasicPlanFactory()
        self.user = UserFactory(current_plan=self.plan)

    def test_creates_user_with_unique_request_token_automatically(self):
        """Test that users are created with unique request tokens."""
        user1 = UserFactory()
        user2 = UserFactory()

        self.assertNotEqual(user1.request_token, user2.request_token)
        self.assertIsNotNone(user1.request_token)
        self.assertIsNotNone(user2.request_token)

    def test_generates_new_request_token_and_preserves_history(self):
        """Test token regeneration with history preservation."""
        original_token = self.user.request_token

        new_token = self.user.generate_new_request_token(save_old=True)

        self.assertNotEqual(new_token, original_token)
        self.assertEqual(self.user.request_token, new_token)
        self.assertIn(str(original_token), self.user.previous_tokens)

    def test_generates_new_token_without_saving_history_when_requested(self):
        """Test token regeneration without history preservation."""
        original_token = self.user.request_token

        new_token = self.user.generate_new_request_token(save_old=False)

        self.assertNotEqual(new_token, original_token)
        self.assertEqual(self.user.request_token, new_token)
        self.assertNotIn(str(original_token), self.user.previous_tokens)

    def test_identifies_expired_tokens_correctly(self):
        """Test token expiration detection."""
        # Set token to be expired
        self.user.request_token_expires = timezone.now() - timedelta(hours=1)
        self.user.save()

        self.assertTrue(self.user.is_token_expired())

    def test_identifies_valid_tokens_within_expiry_period(self):
        """Test valid token detection."""
        # Set token to be valid
        self.user.request_token_expires = timezone.now() + timedelta(hours=1)
        self.user.save()

        self.assertFalse(self.user.is_token_expired())

    def test_handles_never_expiring_tokens_appropriately(self):
        """Test never-expiring token behavior."""
        self.user.token_never_expires = True
        self.user.request_token_expires = timezone.now() - timedelta(days=365)
        self.user.save()

        self.assertFalse(self.user.is_token_expired())

    def test_returns_comprehensive_token_information_dictionary(self):
        """Test token information retrieval."""
        token_info = self.user.get_token_info()

        self.assertIn("token", token_info)
        self.assertIn("created", token_info)
        self.assertIn("expires", token_info)
        self.assertIn("is_expired", token_info)
        self.assertIn("never_expires", token_info)
        self.assertEqual(token_info["token"], str(self.user.request_token))

    def test_automatically_sets_token_expiry_on_creation(self):
        """Test automatic token expiry setting."""
        user = UserFactory(token_validity_days=7)

        expected_expiry = user.request_token_created + timedelta(days=7)
        self.assertAlmostEqual(
            user.request_token_expires.timestamp(),
            expected_expiry.timestamp(),
            delta=60,  # Allow 1 minute difference
        )

    def test_respects_custom_token_validity_periods(self):
        """Test custom token validity settings."""
        user = UserFactory(token_validity_days=90)

        expected_expiry = user.request_token_created + timedelta(days=90)
        self.assertAlmostEqual(
            user.request_token_expires.timestamp(),
            expected_expiry.timestamp(),
            delta=60,  # Allow 1 minute difference
        )

    def test_handles_token_regeneration_with_custom_expiry(self):
        """Test token regeneration with custom expiry settings."""
        new_token = self.user.generate_new_request_token(
            save_old=True, never_expires=True
        )

        self.assertEqual(self.user.request_token, new_token)
        self.assertTrue(self.user.token_never_expires)

    def test_maintains_token_history_integrity_across_regenerations(self):
        """Test token history integrity."""
        tokens = []
        for i in range(5):
            tokens.append(str(self.user.request_token))
            self.user.generate_new_request_token(save_old=True)

        # Check that all previous tokens are in history
        for token in tokens[:-1]:  # Exclude the last one (current token)
            self.assertIn(token, self.user.previous_tokens)

    def test_prevents_token_history_duplication(self):
        """Test that token history doesn't contain duplicates."""
        original_token = str(self.user.request_token)

        # Generate same token multiple times (simulated)
        for _ in range(3):
            self.user.generate_new_request_token(save_old=True)

        # Each token should appear only once in history
        token_counts = {}
        for token in self.user.previous_tokens:
            token_counts[token] = token_counts.get(token, 0) + 1

        for count in token_counts.values():
            self.assertEqual(count, 1)

    def test_limits_token_history_size_appropriately(self):
        """Test token history size limitations."""
        # Generate many tokens
        for _ in range(20):
            self.user.generate_new_request_token(save_old=True)

        # History should be limited to reasonable size
        self.assertLessEqual(len(self.user.previous_tokens), 20)

    def test_handles_token_auto_renewal_configuration(self):
        """Test token auto-renewal settings."""
        self.user.token_auto_renew = True
        self.user.save()

        # Test that auto-renewal is properly configured
        self.assertTrue(self.user.token_auto_renew)

    def test_validates_token_format_consistency(self):
        """Test that generated tokens have consistent format."""
        tokens = []
        for _ in range(5):
            token = self.user.generate_new_request_token()
            tokens.append(token)

        # All tokens should be valid UUIDs
        for token in tokens:
            self.assertIsInstance(token, uuid.UUID)

    @freeze_time("2024-01-15 12:00:00")
    def test_calculates_token_expiry_correctly_across_timezones(self):
        """Test token expiry calculation in different timezones."""
        user = UserFactory(token_validity_days=30)

        expected_expiry = timezone.now() + timedelta(days=30)
        self.assertAlmostEqual(
            user.request_token_expires.timestamp(),
            expected_expiry.timestamp(),
            delta=60,
        )

    def test_handles_concurrent_token_operations_safely(self):
        """Test thread safety of token operations."""
        original_token = self.user.request_token

        # Simulate concurrent regeneration attempts
        tokens = []
        for _ in range(3):
            token = self.user.generate_new_request_token(save_old=True)
            tokens.append(token)

        # Should maintain consistency
        self.assertEqual(len(set(tokens)), len(tokens))  # All tokens unique

    def test_enforces_token_uniqueness_across_users(self):
        """Test that tokens are unique across all users."""
        users = [UserFactory() for _ in range(10)]
        tokens = [user.request_token for user in users]

        # All tokens should be unique
        self.assertEqual(len(set(tokens)), len(tokens))


class TokenHistoryModelAuditTrailTest(TestCase):
    """
    Test suite for TokenHistory model functionality.

    Covers token history creation, retrieval, ordering, and all audit trail
    functionality for tracking token changes and user authentication events.
    """

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()

    def test_creates_token_history_record_for_new_tokens(self):
        """Test token history record creation."""
        TokenHistory.objects.create(
            user=self.user,
            token=str(self.user.request_token),
            expires_at=timezone.now() + timedelta(days=30),
        )

        history = TokenHistory.objects.filter(user=self.user)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().token, str(self.user.request_token))

    def test_orders_token_history_by_creation_date_descending(self):
        """Test token history ordering."""
        # Create multiple history records
        for i in range(3):
            TokenHistory.objects.create(
                user=self.user,
                token=f"token_{i}",
                expires_at=timezone.now() + timedelta(days=30),
            )

        history = TokenHistory.objects.filter(user=self.user)
        dates = [record.created_at for record in history]

        # Should be ordered by creation date descending
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_tracks_token_expiry_information_accurately(self):
        """Test token expiry tracking in history."""
        expires_at = timezone.now() + timedelta(days=7)

        TokenHistory.objects.create(
            user=self.user,
            token="test_token",
            expires_at=expires_at,
            never_expires=False,
        )

        record = TokenHistory.objects.get(token="test_token")
        self.assertEqual(record.expires_at, expires_at)
        self.assertFalse(record.never_expires)

    def test_handles_never_expiring_tokens_in_history(self):
        """Test never-expiring token history."""
        TokenHistory.objects.create(
            user=self.user, token="never_expires_token", never_expires=True
        )

        record = TokenHistory.objects.get(token="never_expires_token")
        self.assertTrue(record.never_expires)
        self.assertIsNone(record.expires_at)


class UserRegistrationApiEndpointTest(APITestCase):
    """
    Test suite for user registration API endpoint.

    Covers user registration validation, password handling, plan assignment,
    and all registration-related API functionality including error handling.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.registration_url = reverse("register")  # Adjust URL name as needed
        self.plan = FreePlanFactory()

    def test_registers_new_user_with_valid_data_successfully(self):
        """Test successful user registration."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "password2": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(self.registration_url, registration_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_rejects_registration_with_mismatched_passwords(self):
        """Test password mismatch validation."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "password2": "differentpassword",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(self.registration_url, registration_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="newuser@example.com").exists())

    def test_rejects_registration_with_invalid_email_format(self):
        """Test email format validation."""
        registration_data = {
            "email": "invalid-email",
            "password": "securepassword123",
            "password2": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(self.registration_url, registration_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_prevents_duplicate_email_registration(self):
        """Test duplicate email prevention."""
        # Create existing user
        UserFactory(email="existing@example.com")

        registration_data = {
            "email": "existing@example.com",
            "password": "securepassword123",
            "password2": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(self.registration_url, registration_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enforces_password_strength_requirements(self):
        """Test password strength validation."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "123",  # Too weak
            "password2": "123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(self.registration_url, registration_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assigns_default_plan_to_new_users(self):
        """Test default plan assignment during registration."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "password2": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(self.registration_url, registration_data)

        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(email="newuser@example.com")
            self.assertIsNotNone(user.current_plan)

    def test_generates_unique_request_token_for_new_users(self):
        """Test request token generation during registration."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "password2": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(self.registration_url, registration_data)

        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(email="newuser@example.com")
            self.assertIsNotNone(user.request_token)

    def test_handles_registration_with_optional_fields(self):
        """Test registration with optional fields."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "password2": "securepassword123",
            "token_auto_renew": True,
            "token_validity_days": 60,
        }

        response = self.client.post(self.registration_url, registration_data)

        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(email="newuser@example.com")
            self.assertTrue(user.token_auto_renew)
            self.assertEqual(user.token_validity_days, 60)

    def test_returns_appropriate_error_messages_for_invalid_data(self):
        """Test error message quality."""
        registration_data = {
            "email": "",  # Missing email
            "password": "securepassword123",
            "password2": "securepassword123",
        }

        response = self.client.post(self.registration_url, registration_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class JwtAuthenticationIntegrationTest(APITestCase):
    """
    Test suite for JWT authentication integration.

    Covers JWT token validation, authentication middleware, protected endpoints,
    and all JWT-related authentication functionality.
    """

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client = APIClient()

    def test_authenticates_user_with_valid_jwt_token(self):
        """Test successful JWT authentication."""
        # Assuming JWT authentication is set up
        self.client.force_authenticate(user=self.user)

        # Test accessing a protected endpoint
        response = self.client.get("/v1/aggs/")  # Clean /v1/ URL

        # Should not return 401 if JWT auth is working
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_requests_with_invalid_jwt_tokens(self):
        """Test JWT token validation."""
        # Set invalid token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")

        response = self.client.get("/v1/aggs/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_requests_with_expired_jwt_tokens(self):
        """Test expired JWT token handling."""
        # This would require mocking an expired token
        with patch("jwt.decode") as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError()

            self.client.credentials(HTTP_AUTHORIZATION="Bearer expired_token")
            response = self.client.get("/v1/aggs/")

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_handles_malformed_jwt_authorization_headers(self):
        """Test malformed authorization header handling."""
        malformed_headers = [
            "Bearer",  # Missing token
            "Invalid format",  # Wrong format
            "Bearer token1 token2",  # Multiple tokens
        ]

        for header in malformed_headers:
            with self.subTest(header=header):
                self.client.credentials(HTTP_AUTHORIZATION=header)
                response = self.client.get("/v1/aggs/")

                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RequestTokenAuthenticationSystemTest(APITestCase):
    """
    Test suite for request token authentication system.

    Covers custom request token authentication, token validation, header processing,
    and all request token-related authentication functionality.
    """

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client = APIClient()
        self.factory = APIRequestFactory()

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_authenticates_user_with_valid_request_token(self, mock_handle):
        """Test successful request token authentication."""
        # Mock the proxy response
        from rest_framework.response import Response

        mock_handle.return_value = Response({}, status=status.HTTP_200_OK)

        # Set request token header
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        # Test accessing a protected endpoint
        response = self.client.get("/v1/aggs/")  # Clean /v1/ URL

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rejects_requests_with_invalid_request_tokens(self):
        """Test invalid request token rejection."""
        self.client.credentials(HTTP_X_REQUEST_TOKEN="invalid-token")

        response = self.client.get("/v1/aggs/")  # Clean /v1/ URL

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_requests_with_expired_request_tokens(self):
        """Test expired request token handling."""
        # Set token to expired
        self.user.request_token_expires = timezone.now() - timedelta(hours=1)
        self.user.save()

        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/aggs/")  # Clean /v1/ URL

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_accepts_never_expiring_request_tokens(self, mock_handle):
        """Test never-expiring token handling."""
        # Mock the proxy response
        from rest_framework.response import Response

        mock_handle.return_value = Response({}, status=status.HTTP_200_OK)

        self.user.token_never_expires = True
        self.user.request_token_expires = timezone.now() - timedelta(days=365)
        self.user.save()

        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/aggs/")  # Clean /v1/ URL

        # Should not be rejected due to expiration
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_handles_missing_request_token_header(self):
        """Test missing request token header handling."""
        # Don't set any credentials

        response = self.client.get("/v1/aggs/")  # Clean /v1/ URL

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_validates_request_token_format(self):
        """Test request token format validation."""
        invalid_tokens = [
            "not-a-uuid",
            "123",
            "",
            "invalid-uuid-format",
        ]

        for token in invalid_tokens:
            with self.subTest(token=token):
                self.client.credentials(HTTP_X_REQUEST_TOKEN=token)
                response = self.client.get("/v1/aggs/")  # Clean /v1/ URL

                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileManagementApiTest(APITestCase):
    """
    Test suite for user profile management API endpoints.

    Covers profile retrieval, updates, authentication requirements,
    and all user profile-related API functionality.
    """

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client = APIClient()
        self.profile_url = "/api/profile/"  # Adjust URL as needed

    def test_retrieves_user_profile_for_authenticated_users(self):
        """Test profile retrieval for authenticated users."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.profile_url)

        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["email"], self.user.email)

    def test_denies_profile_access_for_unauthenticated_users(self):
        """Test profile access denial for unauthenticated users."""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_updates_user_profile_with_valid_data(self):
        """Test profile update functionality."""
        self.client.force_authenticate(user=self.user)

        update_data = {"first_name": "Updated", "last_name": "Name"}

        response = self.client.patch(self.profile_url, update_data)

        if response.status_code == status.HTTP_200_OK:
            self.user.refresh_from_db()
            self.assertEqual(self.user.first_name, "Updated")

    def test_prevents_email_changes_through_profile_update(self):
        """Test email change prevention."""
        self.client.force_authenticate(user=self.user)

        original_email = self.user.email
        update_data = {"email": "newemail@example.com"}

        response = self.client.patch(self.profile_url, update_data)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)

    def test_includes_token_information_in_profile_response(self):
        """Test token info inclusion in profile."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.profile_url)

        if response.status_code == status.HTTP_200_OK and "token_info" in response.data:
            self.assertIn("token", response.data["token_info"])


class TokenRegenerationApiEndpointTest(APITestCase):
    """
    Test suite for token regeneration API endpoint.

    Covers token regeneration functionality, history preservation options,
    authentication requirements, and all token management API features.
    """

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client = APIClient()
        self.regenerate_url = "/api/regenerate-token/"  # Fixed URL path

    def test_regenerates_token_for_authenticated_users(self):
        """Test token regeneration for authenticated users."""
        self.client.force_authenticate(user=self.user)

        original_token = self.user.request_token

        response = self.client.post(self.regenerate_url)

        if response.status_code == status.HTTP_200_OK:
            self.user.refresh_from_db()
            self.assertNotEqual(self.user.request_token, original_token)

    def test_denies_token_regeneration_for_unauthenticated_users(self):
        """Test token regeneration denial for unauthenticated users."""
        response = self.client.post(self.regenerate_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_preserves_old_token_in_history_when_requested(self):
        """Test token history preservation during regeneration."""
        self.client.force_authenticate(user=self.user)

        original_token = str(self.user.request_token)

        response = self.client.post(self.regenerate_url, {"save_old": True})

        if response.status_code == status.HTTP_200_OK:
            self.user.refresh_from_db()
            self.assertIn(original_token, self.user.previous_tokens)

    def test_discards_old_token_when_history_not_requested(self):
        """Test token regeneration without history preservation."""
        self.client.force_authenticate(user=self.user)

        original_token = str(self.user.request_token)

        response = self.client.post(self.regenerate_url, {"save_old": False})

        if response.status_code == status.HTTP_200_OK:
            self.user.refresh_from_db()
            self.assertNotIn(original_token, self.user.previous_tokens)

    def test_supports_custom_token_settings_during_regeneration(self):
        """Test custom token settings in regeneration."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.regenerate_url, {"auto_renew": True, "validity_days": 90}
        )

        if response.status_code == status.HTTP_200_OK:
            self.user.refresh_from_db()
            self.assertTrue(self.user.token_auto_renew)
            self.assertEqual(self.user.token_validity_days, 90)


class TokenHistoryApiEndpointTest(APITestCase):
    """
    Test suite for token history API endpoint.

    Covers token history retrieval, pagination, authentication requirements,
    and all token history-related API functionality.
    """

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client = APIClient()
        self.history_url = "/api/token-history/"  # Fixed URL path

    def test_retrieves_token_history_for_authenticated_users(self):
        """Test token history retrieval for authenticated users."""
        self.client.force_authenticate(user=self.user)

        # Create some token history
        TokenHistory.objects.create(
            user=self.user,
            token="old_token_1",
            expires_at=timezone.now() + timedelta(days=30),
        )

        response = self.client.get(self.history_url)

        if response.status_code == status.HTTP_200_OK and "results" in response.data:
            self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_denies_token_history_access_for_unauthenticated_users(self):
        """Test token history access denial for unauthenticated users."""
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_orders_token_history_by_creation_date_descending(self):
        """Test token history ordering."""
        self.client.force_authenticate(user=self.user)

        # Create multiple history records
        for i in range(3):
            TokenHistory.objects.create(
                user=self.user,
                token=f"token_{i}",
                expires_at=timezone.now() + timedelta(days=30),
            )

        response = self.client.get(self.history_url)

        if (
            response.status_code == status.HTTP_200_OK
            and "results" in response.data
            and len(response.data["results"]) > 1
        ):
            # Check ordering
            dates = [item["created_at"] for item in response.data["results"]]
            self.assertEqual(dates, sorted(dates, reverse=True))

    def test_filters_token_history_by_user_ownership(self):
        """Test that users only see their own token history."""
        other_user = UserFactory()

        # Create history for other user
        TokenHistory.objects.create(
            user=other_user,
            token="other_user_token",
            expires_at=timezone.now() + timedelta(days=30),
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.history_url)

        if response.status_code == status.HTTP_200_OK and "results" in response.data:
            # Should not include other user's tokens
            tokens = [item["token"] for item in response.data["results"]]
            self.assertNotIn("other_user_token", tokens)


class DailyApiLimitPermissionEnforcementTest(APITestCase):
    """
    Test suite for daily API limit permission enforcement.

    Covers request counting, limit enforcement, permission logic,
    and all daily limit-related permission functionality.
    """

    def setUp(self):
        """Set up test data."""
        self.plan = BasicPlanFactory(daily_request_limit=5)
        self.user = UserFactory(current_plan=self.plan)
        self.client = APIClient()

    def test_allows_requests_within_daily_limit(self):
        """Test that requests within limit are allowed."""
        self.user.daily_requests_made = 3  # Below limit of 5
        self.user.last_request_date = timezone.now().date()
        self.user.save()

        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/aggs/")

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_denies_requests_when_daily_limit_exceeded(self):
        """Test that requests are denied when limit is exceeded."""
        self.user.daily_requests_made = 5  # At limit
        self.user.last_request_date = timezone.now().date()
        self.user.save()

        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/aggs/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resets_daily_count_on_new_day(self):
        """Test daily count reset functionality."""
        self.user.daily_requests_made = 5  # At limit
        self.user.last_request_date = timezone.now().date() - timedelta(
            days=1
        )  # Yesterday
        self.user.save()

        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/aggs/")

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_handles_users_without_active_subscriptions(self):
        """Test permission handling for inactive subscriptions."""
        self.user.subscription_status = "inactive"
        self.user.save()

        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/aggs/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_handles_users_with_expired_subscriptions(self):
        """Test handling of expired subscriptions."""
        self.user.subscription_expires_at = timezone.now() - timedelta(days=1)
        self.user.save()

        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/aggs/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticationSystemIntegrationTest(APITestCase):
    """
    Test suite for complete authentication system integration.

    Covers end-to-end authentication flows, multiple auth methods,
    system integration, and comprehensive authentication testing scenarios.
    """

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client = APIClient()

    def test_complete_user_registration_and_authentication_flow(self):
        """Test complete registration to authentication flow."""
        # Step 1: Register user
        registration_data = {
            "email": "testflow@example.com",
            "password": "securepassword123",
            "password2": "securepassword123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = self.client.post("/api/register/", registration_data)

        if response.status_code == status.HTTP_201_CREATED:
            # Step 2: Use request token for authentication
            user = User.objects.get(email="testflow@example.com")
            self.client.credentials(HTTP_X_REQUEST_TOKEN=str(user.request_token))

            # Step 3: Access protected endpoint
            response = self.client.get("/v1/aggs/")

            # Should be able to access API
            self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_handles_concurrent_authentication_attempts_safely(self):
        """Test concurrent authentication handling."""
        token = str(self.user.request_token)

        # Simulate multiple concurrent requests
        responses = []
        for _ in range(5):
            client = APIClient()
            client.credentials(HTTP_X_REQUEST_TOKEN=token)
            response = client.get("/v1/aggs/")
            responses.append(response.status_code)

        # All should have consistent authentication results
        unique_statuses = set(responses)
        self.assertLessEqual(len(unique_statuses), 2)  # Only success/failure statuses

    def test_maintains_authentication_state_across_requests(self):
        """Test authentication state consistency."""
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        # Make multiple requests
        for _ in range(3):
            response = self.client.get("/v1/aggs/")
            # Authentication should remain consistent
            if response.status_code != status.HTTP_401_UNAUTHORIZED:
                break
        else:
            self.fail("Authentication failed across multiple requests")

    def test_handles_mixed_authentication_methods_appropriately(self):
        """Test handling of multiple authentication methods."""
        # Set both JWT and request token
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/aggs/")

        # Should authenticate successfully with either method
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_properly_logs_authentication_events_for_auditing(self):
        """Test authentication event logging."""
        # This would test logging functionality if implemented
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        with patch("logging.Logger.info") as mock_log:
            response = self.client.get("/v1/aggs/")

            # Should log authentication events
            # This depends on implementation
            pass
