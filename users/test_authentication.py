import json
import uuid
from datetime import timedelta, date
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, TokenHistory
from users.serializers import UserRegistrationSerializer, UserSerializer, TokenRegenerationSerializer
from users.views import RegisterView, UserProfileView, RegenerateRequestTokenView, TokenHistoryView
from users.authentication import RequestTokenAuthentication
from users.permissions import DailyLimitPermission

User = get_user_model()


class UserModelTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            daily_request_limit=100
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.daily_request_limit, 100)
        self.assertEqual(self.user.daily_requests_made, 0)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertIsInstance(self.user.request_token, uuid.UUID)

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), 'test@example.com')

    def test_superuser_creation(self):
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_token_generation_on_creation(self):
        self.assertIsNotNone(self.user.request_token)
        self.assertIsNotNone(self.user.request_token_created)

    def test_token_auto_expiry_setting(self):
        self.user.token_auto_renew = False
        self.user.token_validity_days = 30
        self.user.save()
        
        expected_expiry = self.user.request_token_created + timedelta(days=30)
        self.assertAlmostEqual(
            self.user.request_token_expires,
            expected_expiry,
            delta=timedelta(seconds=1)
        )

    def test_never_expire_token_setting(self):
        self.user.token_never_expires = True
        self.user.save()
        self.assertIsNone(self.user.request_token_expires)

    def test_generate_new_request_token(self):
        old_token = self.user.request_token
        old_created = self.user.request_token_created
        
        self.user.generate_new_request_token()
        
        self.assertNotEqual(self.user.request_token, old_token)
        self.assertGreater(self.user.request_token_created, old_created)

    def test_generate_new_token_saves_old_token(self):
        old_token = str(self.user.request_token)
        
        self.user.generate_new_request_token(save_old=True)
        
        self.assertIn(old_token, self.user.previous_tokens)
        
        history = TokenHistory.objects.filter(user=self.user, token=old_token)
        self.assertTrue(history.exists())

    def test_generate_new_token_without_saving_old(self):
        initial_count = len(self.user.previous_tokens)
        
        self.user.generate_new_request_token(save_old=False)
        
        self.assertEqual(len(self.user.previous_tokens), initial_count)

    def test_reset_daily_requests(self):
        self.user.daily_requests_made = 50
        self.user.last_request_date = date.today() - timedelta(days=1)
        
        self.user.reset_daily_requests()
        
        self.assertEqual(self.user.daily_requests_made, 0)
        self.assertEqual(self.user.last_request_date, date.today())

    def test_increment_request_count(self):
        initial_count = self.user.daily_requests_made
        
        self.user.increment_request_count()
        
        self.assertEqual(self.user.daily_requests_made, initial_count + 1)
        self.assertEqual(self.user.last_request_date, date.today())

    def test_has_reached_daily_limit(self):
        self.user.daily_request_limit = 100
        self.user.daily_requests_made = 99
        self.assertFalse(self.user.has_reached_daily_limit())
        
        self.user.daily_requests_made = 100
        self.assertTrue(self.user.has_reached_daily_limit())

    def test_token_expiry_check(self):
        self.user.request_token_expires = timezone.now() + timedelta(hours=1)
        self.assertFalse(self.user.is_token_expired())
        
        self.user.request_token_expires = timezone.now() - timedelta(hours=1)
        self.assertTrue(self.user.is_token_expired())

    def test_never_expire_token_is_not_expired(self):
        self.user.token_never_expires = True
        self.user.request_token_expires = None
        self.assertFalse(self.user.is_token_expired())

    def test_get_token_info(self):
        token_info = self.user.get_token_info()
        
        self.assertIn('token', token_info)
        self.assertIn('created_at', token_info)
        self.assertIn('expires_at', token_info)
        self.assertIn('is_expired', token_info)
        self.assertIn('never_expires', token_info)
        self.assertIn('auto_renew', token_info)


class TokenHistoryModelTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.token_history = TokenHistory.objects.create(
            user=self.user,
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=30)
        )

    def test_token_history_creation(self):
        self.assertEqual(self.token_history.user, self.user)
        self.assertEqual(self.token_history.token, 'test-token-123')
        self.assertTrue(self.token_history.is_active)
        self.assertFalse(self.token_history.never_expires)

    def test_token_history_string_representation(self):
        expected = f"Token for {self.user.email} created at {self.token_history.created_at}"
        self.assertEqual(str(self.token_history), expected)

    def test_token_history_ordering(self):
        older_token = TokenHistory.objects.create(
            user=self.user,
            token='older-token',
            created_at=timezone.now() - timedelta(days=1)
        )
        
        tokens = list(TokenHistory.objects.filter(user=self.user))
        self.assertEqual(tokens[0], self.token_history)
        self.assertEqual(tokens[1], older_token)


class UserRegistrationTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.registration_url = '/api/register/'

    def test_user_registration_success(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.registration_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')

    def test_user_registration_password_mismatch(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'differentpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.registration_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        User.objects.create_user(
            email='existing@example.com',
            password='existingpass123'
        )
        
        data = {
            'email': 'existing@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        
        response = self.client.post(self.registration_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        data = {
            'email': 'invalid-email',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        
        response = self.client.post(self.registration_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_weak_password(self):
        data = {
            'email': 'newuser@example.com',
            'password': '123',
            'password2': '123'
        }
        
        response = self.client.post(self.registration_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTAuthenticationTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_jwt_token_generation(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/token/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        
        data = {'refresh': str(refresh)}
        response = self.client.post('/api/token/refresh/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_jwt_protected_endpoint_access(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_jwt_invalid_token_access(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RequestTokenAuthenticationTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.request_token = str(self.user.request_token)

    def test_request_token_authentication_success(self):
        self.client.credentials(HTTP_X_REQUEST_TOKEN=self.request_token)
        
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_token_authentication_invalid_token(self):
        self.client.credentials(HTTP_X_REQUEST_TOKEN='invalid-token')
        
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_request_token_authentication_expired_token(self):
        self.user.request_token_expires = timezone.now() - timedelta(hours=1)
        self.user.save()
        
        self.client.credentials(HTTP_X_REQUEST_TOKEN=self.request_token)
        
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_request_token_authentication_disabled_user(self):
        self.user.is_active = False
        self.user.save()
        
        self.client.credentials(HTTP_X_REQUEST_TOKEN=self.request_token)
        
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_get_user_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertIn('token_info', response.data)

    def test_update_user_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'token_auto_renew': True,
            'token_validity_days': 60
        }
        
        response = self.client.patch('/api/profile/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.token_auto_renew)
        self.assertEqual(self.user.token_validity_days, 60)

    def test_profile_access_without_authentication(self):
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRegenerationTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_regenerate_token_success(self):
        old_token = str(self.user.request_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'save_old': True,
            'auto_renew': True,
            'validity_days': 45
        }
        
        response = self.client.post('/api/regenerate-token/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('new_token', response.data)
        self.assertIn('token_info', response.data)
        
        self.user.refresh_from_db()
        self.assertNotEqual(str(self.user.request_token), old_token)
        self.assertTrue(self.user.token_auto_renew)
        self.assertEqual(self.user.token_validity_days, 45)

    def test_regenerate_token_without_saving_old(self):
        initial_history_count = TokenHistory.objects.filter(user=self.user).count()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {'save_old': False}
        
        response = self.client.post('/api/regenerate-token/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        final_history_count = TokenHistory.objects.filter(user=self.user).count()
        self.assertEqual(final_history_count, initial_history_count)

    def test_regenerate_token_without_authentication(self):
        response = self.client.post('/api/regenerate-token/', {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenHistoryTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        TokenHistory.objects.create(
            user=self.user,
            token='old-token-1',
            expires_at=timezone.now() + timedelta(days=30)
        )
        TokenHistory.objects.create(
            user=self.user,
            token='old-token-2',
            expires_at=timezone.now() + timedelta(days=60),
            is_active=False
        )

    def test_get_token_history(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get('/api/token-history/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIn('token', response.data['results'][0])
        self.assertIn('created_at', response.data['results'][0])
        self.assertIn('expires_at', response.data['results'][0])
        self.assertIn('is_active', response.data['results'][0])

    def test_token_history_without_authentication(self):
        response = self.client.get('/api/token-history/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DailyLimitPermissionTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            daily_request_limit=2,
            daily_requests_made=0
        )
        self.request_token = str(self.user.request_token)

    def test_daily_limit_allows_requests_under_limit(self):
        self.client.credentials(HTTP_X_REQUEST_TOKEN=self.request_token)
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"results": []}'
            mock_response.json.return_value = {"results": []}
            mock_request.return_value = mock_response
            
            response = self.client.get('/v1/stocks/tickers/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_daily_limit_blocks_requests_over_limit(self):
        self.user.daily_requests_made = self.user.daily_request_limit
        self.user.save()
        
        self.client.credentials(HTTP_X_REQUEST_TOKEN=self.request_token)
        
        response = self.client.get('/v1/stocks/tickers/')
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_daily_limit_resets_on_new_day(self):
        self.user.daily_requests_made = self.user.daily_request_limit
        self.user.last_request_date = date.today() - timedelta(days=1)
        self.user.save()
        
        self.client.credentials(HTTP_X_REQUEST_TOKEN=self.request_token)
        
        with patch('proxy_app.views.requests.Session.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"results": []}'
            mock_response.json.return_value = {"results": []}
            mock_request.return_value = mock_response
            
            response = self.client.get('/v1/stocks/tickers/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            self.user.refresh_from_db()
            self.assertEqual(self.user.daily_requests_made, 1)
            self.assertEqual(self.user.last_request_date, date.today())


class AuthenticationSystemIntegrationTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()

    def test_complete_user_journey(self):
        data = {
            'email': 'journey@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
            'first_name': 'Journey',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        login_data = {
            'email': 'journey@example.com',
            'password': 'securepass123'
        }
        
        token_response = self.client.post('/api/token/', login_data)
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        
        access_token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_response = self.client.get('/api/profile/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['email'], 'journey@example.com')
        
        regenerate_response = self.client.post('/api/regenerate-token/', {'save_old': True})
        self.assertEqual(regenerate_response.status_code, status.HTTP_200_OK)
        
        history_response = self.client.get('/api/token-history/')
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(history_response.data['results']), 1)

    def test_dual_authentication_methods(self):
        user = User.objects.create_user(
            email='dual@example.com',
            password='testpass123'
        )
        
        jwt_refresh = RefreshToken.for_user(user)
        jwt_access = str(jwt_refresh.access_token)
        request_token = str(user.request_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_access}')
        jwt_response = self.client.get('/api/profile/')
        self.assertEqual(jwt_response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_X_REQUEST_TOKEN=request_token)
        token_response = self.client.get('/api/profile/')
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(jwt_response.data['email'], token_response.data['email'])

    def test_token_expiry_and_renewal_flow(self):
        user = User.objects.create_user(
            email='expiry@example.com',
            password='testpass123',
            token_auto_renew=False,
            token_validity_days=1
        )
        
        user.request_token_expires = timezone.now() - timedelta(hours=1)
        user.save()
        
        expired_token = str(user.request_token)
        self.client.credentials(HTTP_X_REQUEST_TOKEN=expired_token)
        
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        jwt_refresh = RefreshToken.for_user(user)
        jwt_access = str(jwt_refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_access}')
        
        regenerate_response = self.client.post('/api/regenerate-token/', {
            'save_old': True,
            'validity_days': 30
        })
        self.assertEqual(regenerate_response.status_code, status.HTTP_200_OK)
        
        new_token = regenerate_response.data['new_token']
        self.client.credentials(HTTP_X_REQUEST_TOKEN=new_token)
        
        new_response = self.client.get('/api/profile/')
        self.assertEqual(new_response.status_code, status.HTTP_200_OK) 