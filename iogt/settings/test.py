from os import getenv

from .base import *


ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('DB_NAME', 'postgres'),
        'USER': getenv('DB_USER', 'postgres'),
        'PASSWORD': getenv('DB_PASSWORD', 'iogt'),
        'HOST': getenv('DB_HOST', 'database'),
        'PORT': getenv('DB_PORT', '5432'),
    }
}
SE_APP_HOST = "django"
SE_HUB_HOST = "selenium-hub"
SE_HUB_PORT = "4444"
SECRET_KEY = "##secret_key_for_testing##"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}
