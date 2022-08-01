from django.conf import settings


def add_vapid_public_key(request):
    return {
        'vapid_public_key': settings.WEBPUSH_SETTINGS.get('VAPID_PUBLIC_KEY'),
    }
