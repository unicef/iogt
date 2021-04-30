from .base import *
from google.cloud import secretmanager


def fetch_secret(client, name):
    return client.access_secret_version(
        name=f'projects/702831353322/secrets/{name}/versions/latest'
    ).payload.data.decode('UTF-8')

secrets_client = secretmanager.SecretManagerServiceClient()

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = fetch_secret(secrets_client, 'secret_key')
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'iogt-311717.appspot.com'
GS_DEFAULT_ACL = 'publicRead'
MEDIA_ROOT = 'media/'
MEDIA_URL = 'https://storage.googleapis.com/iogt-311717.appspot.com/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iogt-mvp',
        'USER': 'iogt',
        'PASSWORD': fetch_secret(secrets_client, 'db_password'),
        'HOST': '/cloudsql/iogt-311717:europe-west4:iogt-mvp',
    }
}
