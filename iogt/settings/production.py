import os
from .base import *

DEBUG = os.getenv('DEBUG') == 'enable'
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '0')),
        'OPTIONS': {
            'sslmode': os.environ.get('DB_SSL_MODE', 'require')
        }
    }
}

WAGTAILTRANSFER_SECRET_KEY = os.environ.get('WAGTAILTRANSFER_SECRET_KEY')
WAGTAILTRANSFER_SOURCES = {
   os.environ.get('WAGTAILTRANSFER_SOURCE_NAME', 'default'): {
      'BASE_URL': os.environ.get('WAGTAILTRANSFER_SOURCE_BASE_URL'),
      'SECRET_KEY': os.environ.get('WAGTAILTRANSFER_SOURCE_SECRET_KEY'),
   },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOG_LEVEL', 'INFO')
    },
}

SITE_VERSION = '2.3.1'

try:
    from .local import *
except ImportError:
    pass
