from django.conf import settings


def matomo_tracking(request):
    return {
        'matomo_tracking': settings.MATOMO_TRACKING,
    }
