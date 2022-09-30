import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_comments_moderation_class():
    try:
        pkg, attr = settings.COMMENT_MODERATION_CLASS.rsplit('.', 1)
        return getattr(importlib.import_module(pkg), attr)
    except (AttributeError, ValueError):
        raise ImproperlyConfigured(
            f"No comments community moderator class found at this path '{settings.COMMENT_MODERATION_CLASS}'")
