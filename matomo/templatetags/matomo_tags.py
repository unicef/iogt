from django import template
from django.conf import settings


register = template.Library()


@register.inclusion_tag("matomo_tracking_tags.html", takes_context=True)
def matomo_tracking_tags(context):
    context.update(
        {
            "tracking_enabled": (
                settings.MATOMO_TRACKING
                and settings.MATOMO_SERVER_URL
                and settings.MATOMO_SITE_ID
            ),
            "matomo_site_id": settings.MATOMO_SITE_ID,
            "matomo_server_url": settings.MATOMO_SERVER_URL,
        }
    )

    additional_site_id = settings.MATOMO_ADDITIONAL_SITE_ID
    if type(additional_site_id) is int and additional_site_id > 0:
        context.update({"matomo_additional_site_id": additional_site_id})

    return context
