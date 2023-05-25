from django import template
from django.conf import settings


register = template.Library()


@register.inclusion_tag('matomo_tracking_code.html', takes_context=True)
def matomo_tracking_tags(context):
    context.update({
        'tracking_enabled': settings.MATOMO_TRACKING,
        'matomo_site_id': settings.MATOMO_SITE_ID,
        'matomo_server_url': settings.MATOMO_SERVER_URL
    })
    return context
