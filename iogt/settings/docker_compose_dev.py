import os
from .dev import *

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch7',
        'URLS': ['http://elasticsearch:9200'],
        'INDEX': 'iogt',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
        'AUTO_UPDATE': True,
        'ATOMIC_REBUILD': True
    }
}


WAGTAILTRANSFER_SECRET_KEY = os.environ.get('WAGTAILTRANSFER_SECRET_KEY')
WAGTAILTRANSFER_SOURCES = {
   'iogt_global': {
      'BASE_URL': os.environ.get('WAGTAILTRANSFER_SOURCE_BASE_URL'),
      'SECRET_KEY': os.environ.get('WAGTAILTRANSFER_SOURCE_SECRET_KEY'),
   },
}

# Uncomment if you want to run Postgres
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST'),
#         'PORT': os.environ.get('DB_PORT'),
#     }
# }
