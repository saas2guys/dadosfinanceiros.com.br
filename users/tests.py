from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class RequestTokenAuthenticationTest(APITestCase):
    """Test the custom request token authentication."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", daily_request_limit=100
        )
        self.client = APIClient()

    def test_authentication_with_valid_token(self):
        """Test that valid request token authenticates user."""
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

        response = self.client.get("/v1/docs/")

        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_authentication_with_invalid_token(self, mock_handle):
        """Test that invalid request token fails authentication."""
        mock_handle.return_value = Response(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )

        self.client.credentials(HTTP_X_REQUEST_TOKEN="invalid-token")

        response = self.client.get("/v1/stocks/AAPL/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_authentication_without_token(self, mock_handle):
        """Test that request without token fails authentication."""
        mock_handle.return_value = Response(
            {"error": "No token"}, status=status.HTTP_401_UNAUTHORIZED
        )

        response = self.client.get("/v1/stocks/AAPL/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DailyLimitPermissionTest(APITestCase):
    """Test the daily limit permission class."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", daily_request_limit=2
        )
        self.client = APIClient()
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_request_increments_daily_count(self, mock_handle):
        """Test that making requests increments the daily count."""
        mock_handle.return_value = Response({"status": "OK"}, status=status.HTTP_200_OK)

        initial_count = self.user.daily_requests_made

        response = self.client.get("/v1/stocks/AAPL/")

        self.user.refresh_from_db()

        self.assertEqual(self.user.daily_requests_made, initial_count + 1)

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_daily_limit_enforcement(self, mock_handle):
        """Test that daily limit is enforced."""
        mock_handle.return_value = Response({"status": "OK"}, status=status.HTTP_200_OK)

        self.user.daily_requests_made = self.user.daily_request_limit
        self.user.save()

        response = self.client.get("/v1/stocks/AAPL/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticationIntegrationTest(APITestCase):
    """Test that the authentication system works end-to-end."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client = APIClient()

    def test_frontend_pages_work_without_auth(self):
        """Test that frontend pages don't require authentication."""
        response = self.client.get("/")
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get("/v1/docs/")
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("proxy_app.views.PolygonProxyView._handle_request")
    def test_api_endpoints_require_auth(self, mock_handle):
        """Test that API endpoints require authentication."""
        mock_handle.return_value = Response(
            {"error": "No auth"}, status=status.HTTP_401_UNAUTHORIZED
        )

        response = self.client.get("/v1/stocks/AAPL/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RequestTokenAuthenticationUnitTest(TestCase):
    """Unit tests for the RequestTokenAuthentication class."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_authentication_class_import(self):
        """Test that the authentication class can be imported."""
        from users.authentication import RequestTokenAuthentication

        auth = RequestTokenAuthentication()
        self.assertIsNotNone(auth)

    def test_permission_class_import(self):
        """Test that the permission class can be imported."""
        from users.permissions import DailyLimitPermission

        perm = DailyLimitPermission()
        self.assertIsNotNone(perm)
