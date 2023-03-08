import math
from django.conf import settings
from django.urls import reverse


def commit_hash(request):
    return {'commit_hash': settings.COMMIT_HASH}


def show_footers(request):
    external_link_root = reverse('external-link')
    start_link = request.path.startswith(external_link_root)
    show_footers_ = True
    if start_link:
        show_footers_ = False
    return {'show_footers': show_footers_}


def cache_timeout(request):
    return {'cache_timeout': math.ceil(settings.CACHE_TIMEOUT / 60)}
