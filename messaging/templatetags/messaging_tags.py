from django import template

from messaging.models import Thread

register = template.Library()


@register.filter
def unread(thread, user):
    """
    Check whether there are any unread messages for a particular thread for a user.
    """
    return bool(thread.user_threads.filter(user=user, is_read=False))


@register.filter
def unread_thread_count(user):
    """
    Return the number of Threads with unread messages for this user, useful for highlighting on an account bar for example.
    """
    return Thread.thread_objects.of_user(user).unread().count()
