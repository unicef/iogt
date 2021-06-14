from .base import *
DEBUG = True
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jjfayj6d=90@@@(rop$98ryt36vuyf3!chtneyoku3_f)*z^h_'

ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# try:
#     from .local import *
# except ImportError:
#     pass