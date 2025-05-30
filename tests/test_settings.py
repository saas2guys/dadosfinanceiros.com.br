"""
Test-specific Django settings configuration.
This file contains settings optimizations for running tests.
"""

from proxy_project.settings import *

# Override settings for testing
DEBUG = False

# Use in-memory SQLite for faster test execution
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster test execution
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Disable logging during tests to reduce noise
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

# Use locmem cache for tests that need cache persistence (like replay attack prevention)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# Use a simple password hasher for faster test execution
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable email sending during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Test-specific Stripe settings
STRIPE_TEST_PUBLISHABLE_KEY = 'pk_test_fake_key_for_testing'
STRIPE_TEST_SECRET_KEY = 'sk_test_fake_key_for_testing'
STRIPE_WEBHOOK_SECRET = 'whsec_fake_webhook_secret_for_testing'

# Disable CSRF for API tests
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.RequestTokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'users.permissions.DailyLimitPermission',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Test-specific secret key
SECRET_KEY = 'test-secret-key-for-testing-only-not-for-production'

# Disable secure settings for testing
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False 