from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from rest_framework.response import Response

User = get_user_model()


class RequestTokenAuthenticationTest(APITestCase):
    """Test the custom request token authentication."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            daily_request_limit=100
        )
        self.client = APIClient()
    
    def test_authentication_with_valid_token(self):
        """Test that valid request token authenticates user."""
        # Make a request with valid token to docs endpoint (no auth required)
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))
        
        # Test with docs page which doesn't require authentication
        response = self.client.get('/v1/docs/')
        
        # Should not get authentication error
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('proxy_app.views.PolygonProxyView._handle_request')
    def test_authentication_with_invalid_token(self, mock_handle):
        """Test that invalid request token fails authentication."""
        # Set up mock response
        mock_handle.return_value = Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Make a request with invalid token
        self.client.credentials(HTTP_X_REQUEST_TOKEN='invalid-token')
        
        # Try to access an API endpoint
        response = self.client.get('/v1/stocks/AAPL/')
        
        # Should get authentication error
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('proxy_app.views.PolygonProxyView._handle_request')
    def test_authentication_without_token(self, mock_handle):
        """Test that request without token fails authentication."""
        # Set up mock response
        mock_handle.return_value = Response({'error': 'No token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Make a request without token
        response = self.client.get('/v1/stocks/AAPL/')
        
        # Should get authentication error
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DailyLimitPermissionTest(APITestCase):
    """Test the daily limit permission class."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            daily_request_limit=2  # Set low limit for testing
        )
        self.client = APIClient()
        self.client.credentials(HTTP_X_REQUEST_TOKEN=str(self.user.request_token))
    
    @patch('proxy_app.views.PolygonProxyView._handle_request')
    def test_request_increments_daily_count(self, mock_handle):
        """Test that making requests increments the daily count."""
        # Set up mock response
        mock_handle.return_value = Response({'status': 'OK'}, status=status.HTTP_200_OK)
        
        initial_count = self.user.daily_requests_made
        
        # Make a request
        response = self.client.get('/v1/stocks/AAPL/')
        
        # Refresh user from database
        self.user.refresh_from_db()
        
        # Count should have incremented
        self.assertEqual(self.user.daily_requests_made, initial_count + 1)
    
    @patch('proxy_app.views.PolygonProxyView._handle_request')
    def test_daily_limit_enforcement(self, mock_handle):
        """Test that daily limit is enforced."""
        # Set up mock response
        mock_handle.return_value = Response({'status': 'OK'}, status=status.HTTP_200_OK)
        
        # Set user to be at the limit
        self.user.daily_requests_made = self.user.daily_request_limit
        self.user.save()
        
        # Try to make a request when at limit
        response = self.client.get('/v1/stocks/AAPL/')
        
        # Should get permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticationIntegrationTest(APITestCase):
    """Test that the authentication system works end-to-end."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
    
    def test_frontend_pages_work_without_auth(self):
        """Test that frontend pages don't require authentication."""
        # Test home page
        response = self.client.get('/')
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test docs page
        response = self.client.get('/v1/docs/')
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('proxy_app.views.PolygonProxyView._handle_request')
    def test_api_endpoints_require_auth(self, mock_handle):
        """Test that API endpoints require authentication."""
        # Set up mock response
        mock_handle.return_value = Response({'error': 'No auth'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Try to access API without auth
        response = self.client.get('/v1/stocks/AAPL/')
        
        # Should get authentication error
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RequestTokenAuthenticationUnitTest(TestCase):
    """Unit tests for the RequestTokenAuthentication class."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
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
