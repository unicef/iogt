from django import template

import messaging.utils as utils


register = template.Library()


@register.filter
def unread(thread, user):
    """
    Check whether there are any unread messages for a particular thread for a user.
    """
    return thread.user_threads.filter(user=user, is_read=False).exists()


@register.inclusion_tag("messaging/tags/quick_reply_form.html")
def render_quick_reply_form(thread, user, text):
    return {
        "thread": thread,
        "user": user,
        "text": text,
    }


@register.inclusion_tag("messaging/tags/chatbot_auth_tokens.html")
def chatbot_auth_tokens():
    return {"tokens": utils.get_auth_tokens()}


@register.filter
def is_chatbot(user):
    return utils.is_chatbot(user)
