from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'jjfayj6d=90@@@(rop$98ryt36vuyf3!chtneyoku3_f)*z^h_'
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
        'PASSWORD': 'rZf?3dH!P&Mb&ra!@x^eE',
        'HOST': '/cloudsql/iogt-311717:europe-west4:iogt-mvp',
    }
}
