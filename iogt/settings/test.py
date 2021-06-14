from .base import *  # noqa

SECRET_KEY = "nAHoNtaAFSBrVJhLbNfzbwMc751QFvby"
DATABASES["default"]["TEST"] = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.test.sqlite3'),
    }
}
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
