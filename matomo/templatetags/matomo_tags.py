from django import template
from django.conf import settings


register = template.Library()


@register.inclusion_tag('matomo_tracking_code.html', takes_context=True)
def matomo_tracking_code(context):
    site_id = settings.MATOMO_SITE_ID
    url = settings.MATOMO_URL

    context.update({
        'site_id': site_id,
        'url': url
    })
    return context
