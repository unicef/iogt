import os
from .base import *

DEBUG = True
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

try:
    from .local import *
except ImportError:
    pass
