from .models import Thread


def user_messages(request):
    context = {}
    if request.user.is_authenticated:
        context["inbox_threads"] = Thread.thread_objects.of_user(request.user).inbox()
        context["unread_threads"] = Thread.thread_objects.of_user(request.user).unread()
    return context
