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

<<<<<<< HEAD
SITE_VERSION = '3.0.10'
=======
SITE_VERSION = '3.0.9-rc.38'
>>>>>>> cc68d5b659c472c1a07bcdd2328d1b8331790dd8

try:
    from .local import *
except ImportError:
    pass
