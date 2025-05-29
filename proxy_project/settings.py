import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-proxy-secret-key-change-in-production"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

# Production domain configuration
ALLOWED_HOSTS = (
    ["*"]
    if DEBUG
    else [
        "dadosfinanceiros.com.br",
        "www.dadosfinanceiros.com.br",
        "api.dadosfinanceiros.com.br",
        "localhost",
        "127.0.0.1",
    ]
)

# CSRF Protection Settings
CSRF_TRUSTED_ORIGINS = (
    [
        "https://dadosfinanceiros.com.br",
        "https://www.dadosfinanceiros.com.br",
        "https://api.dadosfinanceiros.com.br",
    ]
    if not DEBUG
    else [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
)

# Security settings for production
if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True

    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Content type sniffing protection
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # XSS protection
    SECURE_BROWSER_XSS_FILTER = True

    # X-Frame-Options
    X_FRAME_OPTIONS = "DENY"

    # Secure referrer policy
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# CSRF Cookie settings
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_AGE = 31449600  # 1 year
CSRF_COOKIE_DOMAIN = ".dadosfinanceiros.com.br" if not DEBUG else None
CSRF_COOKIE_PATH = "/"
CSRF_USE_SESSIONS = False

# Session settings
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_DOMAIN = ".dadosfinanceiros.com.br" if not DEBUG else None
SESSION_COOKIE_PATH = "/"
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Polygon.io API Configuration
POLYGON_API_KEY = "pl7iW76KJzDoNjg2ngpSeRcJQct4ESbo"
POLYGON_BASE_URL = "https://api.polygon.io"

# Application definition - optimized for proxy-only backend
INSTALLED_APPS = [
    # "daphne",  # MUST BE FIRST for WebSocket support - temporarily disabled
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    # "channels",  # temporarily disabled
    "corsheaders",
    "proxy_app",  # Main proxy application
    "users",  # Add the users app
]

# Minimal middleware for performance
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # Required for admin
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # Keep CSRF protection enabled
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Add this line for language selection
]

# Additional production security settings
if not DEBUG:
    # Add CSP middleware in production
    MIDDLEWARE.insert(1, "django_csp.middleware.CSPMiddleware")

    # Content Security Policy settings
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = (
        "'self'",
        "'unsafe-inline'",
        "https://cdn.tailwindcss.com",
        "https://cdnjs.cloudflare.com",
    )
    CSP_STYLE_SRC = (
        "'self'",
        "'unsafe-inline'",
        "https://cdn.tailwindcss.com",
        "https://cdnjs.cloudflare.com",
    )
    CSP_IMG_SRC = ("'self'", "data:", "https:")
    CSP_FONT_SRC = ("'self'", "https:")
    CSP_CONNECT_SRC = ("'self'", "https://dadosfinanceiros.com.br")
    CSP_FRAME_ANCESTORS = ("'none'",)

    # Force HTTPS in production
    USE_TLS = True

ROOT_URLCONF = "proxy_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "users" / "templates",
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ASGI application for WebSocket support
ASGI_APPLICATION = "proxy_project.asgi.application"

# Database - SQLite for simplicity, change to PostgreSQL for production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Redis configuration for caching and WebSocket channels
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
        },
    }
}

# Channels configuration for WebSocket
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
            "capacity": 1500,
            "expiry": 60,
        },
    },
}

# Environment Configuration
ENV = os.environ.get("ENV", "local")

# Django REST Framework Settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "users.authentication.RequestTokenAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        (
            "rest_framework.permissions.AllowAny"
            if ENV == "local"
            else "rest_framework.permissions.IsAuthenticated"
        ),
    ],
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

# Custom User Model
AUTH_USER_MODEL = "users.User"

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# CORS settings for frontend integration (if needed later)
CORS_ALLOWED_ORIGINS = (
    [
        "https://dadosfinanceiros.com.br",
        "https://www.dadosfinanceiros.com.br",
        "https://api.dadosfinanceiros.com.br",
    ]
    if not DEBUG
    else [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",  # For frontend development
    ]
)

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only for development
CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings for production security
if not DEBUG:
    CORS_ALLOW_METHODS = [
        "DELETE",
        "GET",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    ]

    CORS_ALLOW_HEADERS = [
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "x-request-token",  # For your custom token middleware
    ]

# PROXY MICROSERVICE CONFIGURATION - CHANGE THESE TO YOUR MICROSERVICE URLS
MICROSERVICE_BASE_URL = os.environ.get("MICROSERVICE_BASE_URL", "http://localhost:8001")
MICROSERVICE_WS_URL = os.environ.get(
    "MICROSERVICE_WS_URL", "ws://localhost:8001/ws/stocks/"
)
PROXY_TIMEOUT = 30  # seconds

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("pt-br", "Português"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# The absolute path to the directory where collectstatic will collect static files for deployment
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration for monitoring
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "proxy.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console", "file"] if not DEBUG else ["console"],
        "level": "INFO",
    },
    "loggers": {
        "proxy_app": {
            "handlers": ["console", "file"] if not DEBUG else ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / "logs", exist_ok=True)
