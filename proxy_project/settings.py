import os
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import config
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    "SECRET_KEY", default="django-proxy-secret-key-change-in-production"
)

DEBUG = config("DEBUG", default=False, cast=bool)


if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
        "INSERT_BEFORE": "</body>",
        "HIDE_DJANGO_SQL": False,
        "TAG": "div",
        "ENABLE_STACKTRACES": True,
    }

    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.history.HistoryPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]

ALLOWED_HOSTS = (
    ["*"]
    if DEBUG
    else [
        "financialdata.online",
        "www.financialdata.online",
        "api.financialdata.online",
        "localhost",
        "127.0.0.1",
    ]
)

CSRF_TRUSTED_ORIGINS = (
    [
        "https://financialdata.online",
        "https://www.financialdata.online",
        "https://api.financialdata.online",
    ]
    if not DEBUG
    else [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://financialdata.online",
        "https://www.financialdata.online",
        "https://api.financialdata.online",
    ]
)

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_BROWSER_XSS_FILTER = True

    X_FRAME_OPTIONS = "DENY"

    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_AGE = 31449600
CSRF_COOKIE_DOMAIN = ".financialdata.online" if not DEBUG else None
CSRF_COOKIE_PATH = "/"
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_FAILURE_VIEW = "users.views.csrf_failure_view"

SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_DOMAIN = ".financialdata.online" if not DEBUG else None
SESSION_COOKIE_PATH = "/"
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SAMESITE = "Lax"

POLYGON_BASE_URL = config("POLYGON_BASE_URL", default="https://api.polygon.io")
POLYGON_API_KEY = config("POLYGON_API_KEY", default="your-polygon-api-key-here")

# FMP Ultimate API Configuration
FMP_BASE_URL = config("FMP_BASE_URL", default="https://financialmodelingprep.com/api")
FMP_API_KEY = config("FMP_API_KEY", default="your-fmp-api-key-here")

PROXY_TIMEOUT = config("PROXY_TIMEOUT", default=30, cast=int)
PROXY_DOMAIN = config("PROXY_DOMAIN", default="api.financialdata.online")


STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_LIVE_MODE = config("STRIPE_LIVE_MODE", default=False, cast=bool)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_ratelimit",
    "proxy_app",
    "users",
]


if DEBUG:
    try:
        import django_extensions

        INSTALLED_APPS += ["django_extensions"]

        SHELL_PLUS_PRE_IMPORTS = [
            ("pprint", ["pprint", "pformat"]),
            ("datetime", ["datetime", "date", "time", "timedelta"]),
        ]

        SHELL_PLUS_PRINT_SQL = True
        SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000
    except ImportError:
        pass

    if 'test' not in sys.argv:
        try:
            import debug_toolbar

            INSTALLED_APPS += ["debug_toolbar"]

            INTERNAL_IPS = [
                "127.0.0.1",
                "localhost",
            ]

            DEBUG_TOOLBAR_CONFIG = {
                "SHOW_TOOLBAR_CALLBACK": lambda request: True,
                "INSERT_BEFORE": "</body>",
                "HIDE_DJANGO_SQL": False,
                "TAG": "div",
                "ENABLE_STACKTRACES": True,
                "IS_RUNNING_TESTS": False,
            }

            DEBUG_TOOLBAR_PANELS = [
                "debug_toolbar.panels.history.HistoryPanel",
                "debug_toolbar.panels.versions.VersionsPanel",
                "debug_toolbar.panels.timer.TimerPanel",
                "debug_toolbar.panels.settings.SettingsPanel",
                "debug_toolbar.panels.headers.HeadersPanel",
                "debug_toolbar.panels.request.RequestPanel",
                "debug_toolbar.panels.sql.SQLPanel",
                "debug_toolbar.panels.staticfiles.StaticFilesPanel",
                "debug_toolbar.panels.templates.TemplatesPanel",
                "debug_toolbar.panels.cache.CachePanel",
                "debug_toolbar.panels.signals.SignalsPanel",
                "debug_toolbar.panels.redirects.RedirectsPanel",
                "debug_toolbar.panels.profiling.ProfilingPanel",
            ]
        except ImportError:
            pass

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "users.middleware.DatabaseRateLimitMiddleware",
    "users.middleware.UserRequestCountMiddleware",
    "users.middleware.RateLimitHeaderMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]


if DEBUG and 'test' not in sys.argv:
    try:
        import debug_toolbar

        MIDDLEWARE += [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ]
    except ImportError:
        pass

if not DEBUG:
    MIDDLEWARE.insert(1, "csp.middleware.CSPMiddleware")

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
    CSP_CONNECT_SRC = (
        "'self'",
        "https://financialdata.online",
        "https://www.financialdata.online",
        "https://api.financialdata.online",
    )
    CSP_FRAME_ANCESTORS = ("'none'",)
    CSP_FORM_ACTION = ("'self'",)

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

ASGI_APPLICATION = "proxy_project.asgi.application"


DATABASE_URL = config("DATABASE_URL", default=None)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL, conn_max_age=600, conn_health_checks=True
        )
    }

    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "require",
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

REDIS_URL = config("REDIS_URL", default="redis://127.0.0.1:6379")

if 'test' in sys.argv:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'rate_limit': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"{REDIS_URL}/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            },
        },
        "rate_limit": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "rate_limit_cache",
            "OPTIONS": {
                "MAX_ENTRIES": 100000,  # Prevent unlimited growth
                "CULL_FREQUENCY": 10,   # Clean old entries regularly
            },
        },
    }

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

# Logging configuration for the new financial API system
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'financial_api.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'proxy_app': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'financial_api': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

ENV = config("ENV", default="local")

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

AUTH_USER_MODEL = "users.User"


AUTHENTICATION_BACKENDS = [
    "users.authentication.EmailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]


LOGIN_URL = "login"
LOGIN_REDIRECT_URL = reverse_lazy("profile")
LOGOUT_REDIRECT_URL = "home"

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

CORS_ALLOWED_ORIGINS = (
    [
        "https://financialdata.online",
        "https://www.financialdata.online",
        "https://api.financialdata.online",
    ]
    if not DEBUG
    else [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
    ]
)

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True

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
        "x-request-token",
    ]

MICROSERVICE_BASE_URL = config("MICROSERVICE_BASE_URL", default="http://localhost:8001")
MICROSERVICE_WS_URL = config(
    "MICROSERVICE_WS_URL", default="ws://localhost:8001/ws/stocks/"
)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en"

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

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


TEST_RUNNER = "proxy_project.test_runner.SilentTestRunner"


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
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "users": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "users.stripe_service": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "proxy_app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "proxy_app.views": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "stripe": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

os.makedirs(BASE_DIR / "logs", exist_ok=True)
