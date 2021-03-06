import environ

base_dir = environ.Path(__file__) - 2
src_dir = environ.Path(__file__) - 1

# Add DEBUG=False as default
env = environ.Env(DEBUG=(bool, False))
# Load config, file may be specified in env
config_file = env("CONFIG_FILE", default="config.env")
environ.Env.read_env(base_dir(config_file))

INSTALLED_APPS = [
    # Local
    "authentication",
    "apps.event",
    "apps.article",
    "apps.ticket",
    "apps.seating",
    "apps.user",

    # Django (before 3rd-party)
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "mozilla_django_oidc",
    # Admin theme
    "grappelli",

    # Django (after 3rd-party)
    "django.contrib.admin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "authentication.backends.OidcAuthBackend",
)

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# General
DEBUG = env("DEBUG", default=False)
TEMPLATE_DEBUG = DEBUG
BASE_DIR = base_dir
APP_NAME = "CaG Events"
SITE_NAME = env("SITE_NAME")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
SECRET_KEY = env("SECRET_KEY")
NUM_PROXIES = env("NUM_PROXIES", default=0)
WSGI_APPLICATION = "wsgi.application"
ROOT_URLCONF = "urls"
AUTH_USER_MODEL = "authentication.User"
LOGIN_URL = "/auth/login"
LOGIN_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL_FAILURE = "/login_failure"
LOGOUT_REDIRECT_URL = "/"

# Email
DEFAULT_MAIL = env("DEFAULT_MAIL", default="app@localhost")
SUPPORT_MAIL = env("SUPPORT_MAIL", default="support@localhost")
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
# Mailgun (for django_mailgun.MailgunBackend)
MAILGUN_ACCESS_KEY = env("MAILGUN_ACCESS_KEY", default="")
MAILGUN_SERVER_NAME = env("MAILGUN_SERVER_NAME", default="")

# Security
CSRF_COOKIE_PATH = "/"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", default=True)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", default=True)
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [src_dir("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "libraries": {
                "rest_framework_extras": "template_tags.rest_framework_extras",
            },
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Admin theme
GRAPPELLI_ADMIN_TITLE = SITE_NAME
GRAPPELLI_SWITCH_USER = False

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = base_dir(env("STATIC_DIR", default="static"))

# i18n
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", default="UTC")
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] %(message)s",
        },
        "simple": {
            "format": "[%(levelname)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "error_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": base_dir(env("LOG_DIR", default="log"), "error.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "info_file": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": base_dir(env("LOG_DIR", default="log"), "info.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "debug_file": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": base_dir(env("LOG_DIR", default="log"), "debug.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "error_file", "info_file", "debug_file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "mozilla_django_oidc": {
            "handlers": ["console", "error_file", "info_file", "debug_file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # For front-ends using the Authorization header
        "mozilla_django_oidc.contrib.drf.OIDCAuthentication",
        # For browsing the back-end directly from the web browser
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "common.permissions.IsSuperuser",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework_xml.renderers.XMLRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": env("PAGINATION_SIZE", default=20),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("ANON_THROTTLING", default="50/min"),
        "user": env("USER_THROTTLING", default="500/min"),
    },
}

# OIDC
OIDC_DRF_AUTH_BACKEND = "authentication.backends.OidcAuthBackend"
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = env("OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS", default=(15 * 60))
OIDC_RP_CLIENT_ID = env("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = env("OIDC_RP_CLIENT_SECRET")
OIDC_RP_SIGN_ALGO = env("OIDC_RP_SIGN_ALGO")
OIDC_OP_AUTHORIZATION_ENDPOINT = env("OIDC_OP_AUTHORIZATION_ENDPOINT")
OIDC_OP_TOKEN_ENDPOINT = env("OIDC_OP_TOKEN_ENDPOINT")
OIDC_OP_USER_ENDPOINT = env("OIDC_OP_USER_ENDPOINT")
OIDC_OP_JWKS_ENDPOINT = env("OIDC_OP_JWKS_ENDPOINT")
OIDC_OP_ACCOUNT_ENDPOINT = env("OIDC_OP_ACCOUNT_ENDPOINT")

# App settings
SEATING_GENERATE_IMAGES = env("SEATING_GENERATE_IMAGES", default=False)
