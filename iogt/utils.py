from django.conf import settings


def has_md5_hash(name):
    return bool(settings.HAS_MD5_HASH_REGEX.search(name))
