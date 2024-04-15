from .base import *

WAGTAILADMIN_BASE_URL = 'http://localhost:8000'
DEBUG = True
DEBUG_TOOLBAR_ENABLE = False
SECRET_KEY = '!#secret_key_for_development_only#!'
ALLOWED_HOSTS = ['*']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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
