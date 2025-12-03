# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import re
from datetime import timedelta
from uuid import uuid4

import django.conf.locale
import django.conf.global_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from iogt.patch import *  # noqa: F401, F403
from iogt.settings.profanity_settings import (  # noqa: F401
    COMMENTS_ALLOW_PROFANITIES,
    PROFANITIES_LIST
)

# Monkey patch for deprecated ugettext_lazy used in third-party packages
import django.utils.translation
from django.utils.translation import gettext_lazy

# Patch only if missing (for Django 4+ compatibility with old packages)
if not hasattr(django.utils.translation, 'ugettext_lazy'):
    django.utils.translation.ugettext_lazy = gettext_lazy


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)
INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'comments',
    'common',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_comments',
    'django_comments_xtd',
    'django_filters',
    'drf_yasg',
    'generic_chooser',
    'health_check',
    'health_check.cache',
    'health_check.contrib.migrations',
    'health_check.db',
    'health_check.storage',
    'home',
    'interactive',
    'iogt_content_migration',
    'iogt_users',
    'matomo',
    'messaging',
    'modelcluster',
    'admin_notifications',
    'user_notifications',
    'notifications',
    'questionnaires',
    'rest_framework',
    'rest_framework_simplejwt',
    'sass_processor',
    'search',
    'taggit',
    'translation_manager',
    'wagtailautocomplete',
    'wagtail',
    'wagtail.admin',
    'wagtail.contrib.forms',
    'wagtail_modeladmin',
    'wagtail.contrib.redirects',
    'wagtail.contrib.settings',
    'wagtail.documents',
    'wagtail.embeds',
    'wagtail.images',
    'wagtail.search',
    'wagtail.sites',
    'wagtail.snippets',
    "iogt.apps.CustomUsersAppConfig",
    # 'wagtail.users',
    'wagtail_localize',
    'wagtail_localize.locales',
    'wagtail_transfer',
    'wagtailcache',
    'wagtailmarkdown',
    'wagtailmedia',
    'wagtailmenus',
    'wagtailsvg',
    'webpush',
    'wagtail.contrib.search_promotions',
    'admin_login',
    'email_service',
]

# The order of middleware is very important. Take care when modifying this list.
MIDDLEWARE = [
    'wagtailcache.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "iogt.middleware.LocaleMiddleware",
    "iogt.middleware.AdminLocaleMiddleware",
    'iogt.middleware.CustomRedirectMiddleware',
    'iogt_users.middlewares.RegistrationSurveyRedirectMiddleware',
    'external_links.middleware.RewriteExternalLinksMiddleware',
    'iogt.middleware.GlobalDataMiddleware',
    # 'admin_login.middleware.CustomAdminLoginRequiredMiddleware',
    'wagtailcache.cache.FetchFromCacheMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    'admin_login.middleware.EnforceB2CForAdminMiddleware',
]

# Prevent Wagtail's built in menu from showing in Admin > Settings
WAGTAILMENUS_MAIN_MENUS_EDITABLE_IN_WAGTAILADMIN = False

ROOT_URLCONF = 'iogt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "wagtail.contrib.settings.context_processors.settings",
                'wagtailmenus.context_processors.wagtailmenus',
                'wagtail.contrib.settings.context_processors.settings',
                'django.template.context_processors.i18n',
                'home.processors.commit_hash',
                'home.processors.show_footers',
                'messaging.processors.add_vapid_public_key',
                'admin_notifications.processors.push_notification',
                'home.processors.jquery',
            ],
        },
    },
]

WSGI_APPLICATION = 'iogt.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Authentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'admin_login.azure_backend.AzureADBackend',# Default Django backend
)

AUTH_USER_MODEL = 'iogt_users.User'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4
        }
    }
]

# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SASS_PROCESSOR_ROOT = os.path.join(BASE_DIR, 'static')

# Control the forms that django-allauth uses
ACCOUNT_FORMS = {
    "login": "allauth.account.forms.LoginForm",
    "add_email": "allauth.account.forms.AddEmailForm",
    "change_password": "iogt_users.forms.ChangePasswordForm",
    "set_password": "allauth.account.forms.SetPasswordForm",
    "reset_password": "allauth.account.forms.ResetPasswordForm",
    "reset_password_from_key": "allauth.account.forms.ResetPasswordKeyForm",
    "disconnect": "allauth.socialaccount.forms.DisconnectForm",
    # Use our custom signup form
    "signup": "iogt_users.forms.AccountSignupForm",
}

# Wagtail settings
WAGTAIL_SITE_NAME = "IoGT"
ACCOUNT_ADAPTER = 'iogt_users.adapters.AccountAdapter'
WAGTAIL_USER_EDIT_FORM = 'iogt_users.forms.WagtailAdminUserEditForm'
WAGTAIL_USER_CREATION_FORM = 'iogt_users.forms.WagtailAdminUserCreateForm'
WAGTAIL_USER_CUSTOM_FIELDS = [
    'display_name',
    'first_name',
    'last_name',
    'email',
    'terms_accepted'
]

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = os.getenv('BASE_URL', '')

SITE_ID = 1

#Notifications
DJANGO_NOTIFICATIONS_CONFIG = { 'USE_JSONFIELD': True}

# Comments
COMMENTS_APP = 'django_comments_xtd'
COMMENTS_XTD_MAX_THREAD_LEVEL = 1

# Miscellaneous
LOGIN_REDIRECT_URL = "user_profile"
ACCOUNT_LOGOUT_REDIRECT_URL = "logout_redirect"
LOGIN_URL = 'account_login'
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL

# Make Wagtail admin always use your B2C login view for its login challenges
WAGTAIL_LOGIN_URL = 'wagtailadmin_login'   # your: path('admin/login/', AzureADSignupView.as_view(), name='wagtailadmin_loginsssss')

# To help obfuscating comments before they are sent for confirmation
COMMENTS_XTD_SALT = (
    b"Timendi causa est nescire. "
    b"Aequam memento rebus in arduis servare mentem."
)

# Source mail address used for notifications.
COMMENTS_XTD_FROM_EMAIL = "noreply@example.com"

# Contact mail address to show in messages.
COMMENTS_XTD_CONTACT_EMAIL = "helpdesk@example.com"

COMMENTS_XTD_CONFIRM_EMAIL = False

COMMENTS_XTD_FORM_CLASS = 'comments.forms.CommentForm'

COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'default': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
        'who_can_post': 'users'
    }
}

WAGTAIL_I18N_ENABLED = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('ar', _('Arabic')),
    ('bn', _('Bengali')),
    ('ny', _('Chichewa')),  # previously 'ch'
    ('prs', _('Dari')),
    ('en', _('English')),
    ('fa', _('Farsi')),
    ('fr', _('French')),
    ('hi', _('Hindi')),
    ('id', _('Indonesian')),
    ('kaa', _('Karakalpak')),
    ('km', _('Khmer')),
    ('rw', _('Kinyarwanda')),
    ('rn', _('Kirundi')),
    ('ku', _('Kurdish')),
    ('mg', _('Malagasy')),
    ('my', _('Burmese')),
    ('ne', _('Nepali')),
    ('nr', _('Ndebele')),
    ('ps', _('Pashto')),
    ('pt', _('Portuguese')),
    ('qu', _('Quechua')),
    ('ru', _('Russian')),
    ('sn', _('Shona')),  # previously 'sho'
    ('si', _('Sinhala')),
    ('es', _('Spanish')),
    ('sw', _('Swahili')),
    ('tg', _('Tajik')),
    ('ta', _('Tamil')),
    ('ti', _('Tigrinya')),
    ('tr', _('Turkish')),
    ('uk', _('Ukraine')),
    ('ur', _('Urdu')),
    ('uz', _('Uzbek')),
    ('zu', _('Zulu')),
    ('xy', _('Testing')),
    ('ha', _('Hausa')),
    ('yo', _('Yoruba')),
    ('ig', _('Igbo')),
    ('pcm', _('Pidgin')),
    
]

EXTRA_LANG_INFO = {
    'bn': {
        'bidi': False,
        'code': 'bn',
        'name': 'Bengali',
        'name_local': 'Bengali'
    },
    'ku': {
        'bidi': False,
        'code': 'ku',
        'name': 'Kurdish',
        'name_local': 'Kurdish'
    },
    'kaa': {
        'bidi': False,
        'code': 'kaa',
        'name': 'Karakalpak',
        'name_local': 'Karakalpak'
    },
    'mg': {
        'bidi': False,
        'code': 'mg',
        'name': 'Malagasy',
        'name_local': 'Malagasy',
    },
    'nr': {
        'bidi': False,
        'code': 'nr',
        'name': 'Ndebele',
        'name_local': 'Ndebele',
    },
    'ny': {
        'bidi': False,
        'code': 'ny',
        'name': 'Chichewa',
        'name_local': 'Chichewa',
    },
    'qu': {
        'bidi': False,
        'code': 'qu',
        'name': 'Quechua',
        'name_local': 'Quechua',
    },
    'prs': {
        'bidi': True,
        'code': 'prs',
        'name': 'Dari',
        'name_local': 'Dari',
    },
    'ps': {
        'bidi': True,
        'code': 'ps',
        'name': 'Pashto',
        'name_local': 'Pashto',
    },
    'rn': {
        'bidi': False,
        'code': 'rn',
        'name': 'Kirundi',
        'name_local': 'Ikirundi',
    },
    'rw': {
        'bidi': False,
        'code': 'rw',
        'name': 'Kinyarwanda',
        'name_local': 'Kinyarwanda',
    },
    'sn': {
        'bidi': False,
        'code': 'sn',
        'name': 'Shona',
        'name_local': 'Shona',
    },
    'si': {
        'bidi': False,
        'code': 'si',
        'name': 'Sinhala',
        'name_local': 'Sinhala',
    },
    'ti': {
        'bidi': False,
        'code': 'ti',
        'name': 'Tigrinya',
        'name_local': 'Tigrinya',
    },
    'zu': {
        'bidi': False,
        'code': 'zu',
        'name': 'Zulu',
        'name_local': 'Zulu',
    },
    'xy': {
        'bidi': False,
        'code': 'xy',
        'name': 'Testing',
        'name_local': 'Testing',
    },
    'ha': {
        'bidi': False,
        'code': 'ha',
        'name': 'Hausa',
        'name_local': 'Hausa',
    },
    'yo': {
        'bidi': False,
        'code': 'yo',
        'name': 'Yoruba',
        'name_local': 'Yoruba',
    },
    'pcm': {
        'bidi': False,
        'code': 'pcm',
        'name': 'Pidgin',
        'name_local': 'Pidgin',
    },
}

django.conf.locale.LANG_INFO.update(EXTRA_LANG_INFO)

LANGUAGES_BIDI = django.conf.global_settings.LANGUAGES_BIDI + ["ps", "prs"]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

TRANSLATIONS_BASE_DIR = BASE_DIR

# ========= Rapid Pro =================
RAPIDPRO_BOT_GROUP_NAME = os.getenv('RAPIDPRO_BOT_GROUP_NAME', 'rapidpro_chatbot')

WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME = 'iogt_flat_menu_items'

WAGTAIL_RICH_TEXT_FIELD_FEATURES = [
    'h2', 'h3', 'h4',
    'bold', 'italic',
    'ol', 'ul',
    'hr',
    'link',
    'document-link',
    'image',
]

# Search results
SEARCH_RESULTS_PER_PAGE = 10

COMMIT_HASH = os.getenv('COMMIT_HASH')

EXPORT_FILENAME_TIMESTAMP_FORMAT = '%Y-%m-%dT%H%M%S'

WAGTAILMARKDOWN = {
    "allowed_tags": ["i", "b"],
    "autodownload_fontawesome": False,
}

TRANSLATIONS_PROJECT_BASE_DIR = BASE_DIR

WAGTAILTRANSFER_LOOKUP_FIELDS = {
    'auth.permission': ['codename'],
    'contenttypes.contenttype': ['app_label', 'model'],
    'iogt_users.user': ['username'],
    'taggit.tag': ['slug'],
    'wagtailcore.locale': ['language_code'],
}
WAGTAILTRANSFER_NO_FOLLOW_MODELS = [
    'contenttypes.contenttype',
    'wagtailcore.page',
]
WAGTAILTRANSFER_SECRET_KEY = os.getenv('WAGTAILTRANSFER_SECRET_KEY')
WAGTAILTRANSFER_SHOW_ERROR_FOR_REFERENCED_PAGES = True
WAGTAILTRANSFER_SOURCES = {
   os.getenv('WAGTAILTRANSFER_SOURCE_NAME', 'default'): {
      'BASE_URL': os.getenv('WAGTAILTRANSFER_SOURCE_BASE_URL'),
      'SECRET_KEY': os.getenv('WAGTAILTRANSFER_SOURCE_SECRET_KEY'),
   },
}
WAGTAILTRANSFER_UPDATE_RELATED_MODELS = ['wagtailimages.image', 'wagtailsvg.svg',]

REST_FRAMEWORK = {
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S.%fZ',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365),
}

CACHE = os.getenv('CACHE', '') == 'enable'
if CACHE:
    CACHE_LOCATION = os.getenv('CACHE_LOCATION')
    if not CACHE_LOCATION:
        raise ImproperlyConfigured(
            "CACHE_LOCATION must be set if CACHE is set to 'enable'")
    CACHE_BACKEND = os.getenv(
        'CACHE_BACKEND',
        'django_redis.cache.RedisCache')
    DJANGO_REDIS_IGNORE_EXCEPTIONS = True
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    WAGTAIL_CACHE = True
    WAGTAIL_CACHE_BACKEND = 'pagecache'
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))
    KEY_PREFIX = os.getenv('CACHE_KEY_PREFIX', str(uuid4()))
    CACHES = {
        'default': {
            'BACKEND': CACHE_BACKEND,
            'LOCATION': CACHE_LOCATION,
            'TIMEOUT': CACHE_TIMEOUT,
            'KEY_PREFIX': f'{KEY_PREFIX}_default',
        },
        # See 'Caching image renditions' in Wagtail docs
        'renditions': {
            'BACKEND': CACHE_BACKEND,
            'LOCATION': CACHE_LOCATION,
            'TIMEOUT': CACHE_TIMEOUT,
            'KEY_PREFIX': f'{KEY_PREFIX}_renditions',
        },
        'pagecache': {
            'BACKEND': CACHE_BACKEND,
            'LOCATION': CACHE_LOCATION,
            'TIMEOUT': CACHE_TIMEOUT,
            'KEY_PREFIX': f'{KEY_PREFIX}_pagecache',
        },
    }
else:
    WAGTAIL_CACHE = False
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SITE_VERSION = os.getenv('SITE_VERSION', 'unknown')

HAS_MD5_HASH_REGEX = re.compile(r"\.[a-f0-9]{12}\..*$")

WEBPUSH_SETTINGS = {
    'VAPID_PUBLIC_KEY': os.getenv('VAPID_PUBLIC_KEY'),
    'VAPID_PRIVATE_KEY': os.getenv('VAPID_PRIVATE_KEY'),
    'VAPID_ADMIN_EMAIL': os.getenv('VAPID_ADMIN_EMAIL'),
}

COMMENTS_COMMUNITY_MODERATION = os.getenv('COMMENTS_COMMUNITY_MODERATION') == 'enable'
COMMENT_MODERATION_CLASS = os.getenv(
    'COMMENT_MODERATION_CLASS',
    'comments.clients.AlwaysApproveModerator',
)
BLACKLISTED_WORDS = os.getenv('BLACKLISTED_WORDS', '').split(',')

SUPERSET_BASE_URL = os.getenv('SUPERSET_BASE_URL')
SUPERSET_DATABASE_NAME = os.getenv('SUPERSET_DATABASE_NAME')
SUPERSET_USERNAME = os.getenv('SUPERSET_USERNAME')
SUPERSET_PASSWORD = os.getenv('SUPERSET_PASSWORD')

PUSH_NOTIFICATION = os.getenv('PUSH_NOTIFICATION', 'disable') == 'enable'
JQUERY = os.getenv('JQUERY', 'enable') == 'enable'

DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.getenv('DATA_UPLOAD_MAX_NUMBER_FIELDS', '1000'))

# Matomo tracking server and site information
MATOMO_ADDITIONAL_SITE_ID = int(os.getenv('MATOMO_ADDITIONAL_SITE_ID', '0'))
MATOMO_CREATE_VISITOR_ID = os.getenv('MATOMO_CREATE_VISITOR_ID', 'disable') == 'enable'
MATOMO_SERVER_URL = os.getenv('MATOMO_SERVER_URL', '')
MATOMO_SITE_ID = int(os.getenv('MATOMO_SITE_ID', '0'))
MATOMO_TRACKING = os.getenv('MATOMO_TRACKING', 'disable') == 'enable'

# Width size options are 360, 750
IMAGE_SIZE_PRESET = int(os.getenv('IMAGE_SIZE_PRESET', '360'))

# Default primary key field type introduced in Django 3.2 or later versions
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

WAGTAILREDIRECTS_AUTO_CREATE = (
    os.getenv('WAGTAILREDIRECTS_AUTO_CREATE', 'enable') == 'enable'
)
WAGTAILSVG_UPLOAD_FOLDER = "media"

DEFAULT_FROM_EMAIL = os.getenv("EMAIL_FROM", "IoGT <iogt@localhost>")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "disable") == "enable"



# Azure AD B2C set up starts
AZURE_AD_TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
AZURE_AD_SIGNUP_SIGNIN_POLICY = os.getenv("AZURE_AD_SIGNUP_SIGNIN_POLICY")

CURRENT_DOMAIN = os.getenv('CURRENT_DOMAIN')

SOCIALACCOUNT_PROVIDERS = {
        'azure': {  # Use 'azure' as the key here
            'APP': {
                'client_id': os.getenv('AZURE_AD_CLIENT_ID'),
                'secret': os.getenv('AZURE_AD_SECRET_ID'),
            },
            'AZURE_AD_TENANT_ID': os.getenv('AZURE_AD_TENANT_ID'),
            'AZURE_AD_SIGNUP_SIGNIN_POLICY': os.getenv('AZURE_AD_SIGNUP_SIGNIN_POLICY'),
            'SERVER_URL': f"https://{os.getenv('AZURE_AD_TENANT_ID')}.b2clogin.com/{os.getenv('AZURE_AD_TENANT_ID')}.onmicrosoft.com/v2.0/.well-known/openid-configuration?p={os.getenv('AZURE_AD_SIGNUP_SIGNIN_POLICY')}",
            'REDIRECT_URI': f"{CURRENT_DOMAIN}/admin-login/signup-as-admin/callback/",
            'SCOPES': ['openid', 'email', 'profile'],
            'VERIFY_SSL': True,  # SSL verification
            'KEY': 'azure',  # Set 'azure' as the key
        },
}
# Azure AD B2C setup ends
print("CURRENT_DOMAIN", CURRENT_DOMAIN)
print("AZURE_AD_TENANT_ID", AZURE_AD_TENANT_ID)

# Mailjet setup for sending emails
MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
MAILJET_API_SECRET = os.getenv('MAILJET_API_SECRET')
MAILJET_FROM_EMAIL = os.getenv('MAILJET_FROM_EMAIL')
MAILJET_FROM_NAME = os.getenv('MAILJET_FROM_NAME')

# Secure session and CSRF cookies
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

CELERY_BROKER_URL = os.getenv('CACHE_LOCATION')
CELERY_RESULT_BACKEND = os.getenv('CACHE_LOCATION')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
# Enforce HTTPS and HSTS
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Ensure Django trusts the proxy (if applicable)
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
