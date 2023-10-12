from uuid import uuid4

from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("matomo_tracking_tags.html", takes_context=True)
def matomo_tracking_tags(context):
    server_url = settings.MATOMO_SERVER_URL
    site_id = settings.MATOMO_SITE_ID
    uid = user_tracking_id(context["request"].session)

    context.update(
        {
            "tracking_enabled": (settings.MATOMO_TRACKING and server_url and site_id),
            "matomo_site_id": site_id,
            "matomo_server_url": server_url,
            "matomo_image_tracker_url": image_tracker(server_url, site_id, uid),
        }
    )

    additional_site_id = settings.MATOMO_ADDITIONAL_SITE_ID
    if type(additional_site_id) is int and additional_site_id > 0:
        context.update(
            {
                "matomo_additional_site_id": additional_site_id,
                "matomo_additional_image_tracker_url": image_tracker(
                    server_url, additional_site_id, uid
                ),
            }
        )

    return context


def user_tracking_id(session):
    if not session.get("tid"):
        session["tid"] = str(uuid4())

    return session["tid"]


def image_tracker(server_url, site_id, uid):
    return f"{server_url}matomo.php?idsite={site_id}&rec=1&uid={uid}"
