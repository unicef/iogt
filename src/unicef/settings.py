from iogt.settings.docker import *

REFERRER_POLICY = "origin"

MIDDLEWARE_CLASSES += ['unicef.middleware.ReferrerPolicyMiddleware']
if 'iogt.middleware.FaceBookPixelHistoryCounter' in MIDDLEWARE_CLASSES:
    MIDDLEWARE_CLASSES.remove('iogt.middleware.FaceBookPixelHistoryCounter')

INSTALLED_APPS.insert(0, 'unicef')
TEMPLATES[0]['DIRS'] = ['iogt/templates/']
