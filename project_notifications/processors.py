from django.conf import settings


def push_notification(request):
    return {
        'push_notification': settings.PUSH_NOTIFICATION,
    }
