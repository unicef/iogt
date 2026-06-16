from .base import *
from os import getenv

WAGTAILADMIN_BASE_URL = 'http://localhost:8000'
DEBUG = True
DEBUG_TOOLBAR_ENABLE = False
SECRET_KEY = '!#secret_key_for_development_only#!'
ALLOWED_HOSTS = ['*']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Override secure cookie settings for local HTTP development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SECURE_SSL_REDIRECT = False

# ---------------------------------------------------------------------------
# Disable Azure AD B2C enforcement for local development
# This allows superusers to log into Wagtail admin with username/password.
# ---------------------------------------------------------------------------
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'admin_login.middleware.EnforceB2CForAdminMiddleware']

# Reset WAGTAIL_LOGIN_URL so Wagtail uses its own built-in login view
WAGTAIL_LOGIN_URL = 'wagtailadmin_login'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('DB_NAME'),
        'USER': getenv('DB_USER'),
        'PASSWORD': getenv('DB_PASSWORD'),
        'HOST': getenv('DB_HOST'),
        'PORT': getenv('DB_PORT'),
    }
}

if DEBUG and DEBUG_TOOLBAR_ENABLE:
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

    INTERNAL_IPS = ("127.0.0.1",)
    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": False,
        "SHOW_TOOLBAR_CALLBACK": lambda *x: True,
    }

INSTALLED_APPS += ("django_extensions",)

try:
    from .local import *
except ImportError:
    pass
