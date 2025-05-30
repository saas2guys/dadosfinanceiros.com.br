from unittest.mock import MagicMock, patch
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase

from users.models import Plan

User = get_user_model()


class RequestTokenAuthenticationFlowTest(APITestCase):
    """
    Test suite for the request token authentication system.
    
    Validates that the custom request token authentication works correctly,
    including token validation, invalid token handling, and unauthenticated access.
    Tests the core authentication mechanism used for API access.
    """

    def setUp(self):
        # Create a plan first
        self.plan = Plan.objects.create(
            name="Test Plan",
            slug="test-plan",
            daily_request_limit=100,
            price_monthly=Decimal('10.00')
        )
        
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.user.current_plan = self.plan
        self.user.subscription_status = 'active'
        self.user.save()
        
        self.client = APIClient()

    def test_valid_request_token_allows_api_access(self):
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))
        
        with patch("proxy_app.views.PolygonProxyView._handle_request") as mock_handle:
            mock_handle.return_value = Response({}, status=status.HTTP_200_OK)
            response = self.client.get("/v1/us/stocks/AAPL/")
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_invalid_request_token_returns_unauthorized(self, mock_handle):
        mock_handle.return_value = Response({}, status=status.HTTP_200_OK)
        
        # Set invalid token
        self.client.credentials(HTTP_X_REQUEST_TOKEN="invalid-token")
        
        response = self.client.get("/v1/us/stocks/AAPL/")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_handle.assert_not_called()

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_missing_request_token_returns_unauthorized(self, mock_handle):
        mock_handle.return_value = Response({}, status=status.HTTP_200_OK)
        
        # No token set
        response = self.client.get("/v1/us/stocks/AAPL/")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_handle.assert_not_called()


class DailyApiLimitEnforcementTest(APITestCase):
    """
    Test suite for daily API request limit enforcement.
    
    Validates the permission system that tracks and enforces daily request limits
    based on user subscription plans. Tests request counting, limit enforcement,
    and proper handling of limit violations.
    """

    def setUp(self):
        # Create a plan first
        self.plan = Plan.objects.create(
            name="Test Plan", 
            slug="test-plan",
            daily_request_limit=2,
            price_monthly=Decimal('10.00')
        )
        
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.user.current_plan = self.plan
        self.user.subscription_status = 'active'
        self.user.save()
        
        self.client = APIClient()
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_successful_request_increments_daily_count(self, mock_handle):
        mock_handle.return_value = Response({"status": "OK"}, status=status.HTTP_200_OK)

        initial_count = self.user.daily_requests_made
        response = self.client.get("/v1/us/stocks/AAPL/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.daily_requests_made, initial_count + 1)

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_user_at_daily_limit_receives_forbidden(self, mock_handle):
        mock_handle.return_value = Response({"status": "OK"}, status=status.HTTP_200_OK)

        # Set user at daily limit with today's date so count doesn't get reset
        self.user.daily_requests_made = self.user.daily_request_limit
        self.user.last_request_date = timezone.now().date()
        self.user.save()

        response = self.client.get("/v1/us/stocks/AAPL/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ApiAuthenticationIntegrationTest(APITestCase):
    """
    Test suite for overall API authentication integration.
    
    Validates the complete authentication flow including frontend page access
    without authentication and API endpoint protection. Tests the integration
    between different authentication components.
    """

    def setUp(self):
        self.client = APIClient()

    def test_frontend_pages_accessible_without_authentication(self):
        """Frontend pages should be accessible without API authentication"""
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 302])  # Allow redirects
        
    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_api_endpoints_require_valid_authentication(self, mock_handle):
        mock_handle.return_value = Response({}, status=status.HTTP_200_OK)
        
        # Test API endpoint without authentication
        response = self.client.get("/v1/us/stocks/AAPL/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Mock handle should not be called if authentication fails
        mock_handle.assert_not_called()


class RequestTokenAuthenticationUnitTest(TestCase):
    """
    Test suite for request token authentication component isolation.
    
    Unit tests for the authentication classes and permissions in isolation,
    ensuring proper imports and class definitions exist. Tests the individual
    components without integration dependencies.
    """

    def setUp(self):
        self.client = APIClient()

    def test_request_token_authentication_class_can_be_imported(self):
        """Verify authentication class exists and can be imported"""
        try:
            from users.authentication import RequestTokenAuthentication
            self.assertTrue(True, "Authentication class imported successfully")
        except ImportError:
            self.fail("RequestTokenAuthentication class could not be imported")

    def test_daily_limit_permission_class_can_be_imported(self):
        """Verify permission class exists and can be imported"""
        try:
            from users.permissions import DailyLimitPermission
            self.assertTrue(True, "Permission class imported successfully")
        except ImportError:
            self.fail("DailyLimitPermission class could not be imported") 