from django.conf import settings


def show_welcome_banner(request):
    return {
        "first_time_user": request.session.get("first_time_user", True)
    }


def commit_hash(request):
    return {'commit_hash': settings.COMMIT_HASH}
