import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_community_moderation_class():
    try:
        pkg, attr = settings.COMMENTS_COMMUNITY_MODERATOR_CLASS.rsplit('.', 1)
        return getattr(importlib.import_module(pkg), attr)
    except (AttributeError, ValueError):
        raise ImproperlyConfigured(
            f"No comments community moderator class found at this path '{settings.COMMENTS_COMMUNITY_MODERATOR_CLASS}'")
