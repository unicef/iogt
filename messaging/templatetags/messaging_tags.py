from django import template
from django.contrib.auth import get_user_model

register = template.Library()
User = get_user_model()

@register.filter
def unread(thread, user):
    """
    Check whether there are any unread messages for a particular thread for a user.
    """
    return thread.user_threads.filter(user=user, is_read=False).exists()


@register.inclusion_tag('messaging/tags/quick_reply_form.html')
def render_quick_reply_form(thread, user, text):
    return {
        'thread': thread,
        'user': user,
        'text': text,
    }


@register.simple_tag
def chatbot_auth_header():
    return User.get_rapidpro_bot_auth_header()
