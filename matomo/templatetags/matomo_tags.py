from uuid import uuid4
from hashlib import sha1
from datetime import datetime

from django import template
from django.conf import settings


VISITOR_ID_KEY = "vid"
register = template.Library()


@register.inclusion_tag("matomo_tracking_tags.html", takes_context=True)
def matomo_tracking_tags(context):
    server_url = settings.MATOMO_SERVER_URL
    site_id = settings.MATOMO_SITE_ID
    vid = visitor_id(context["request"])

    context.update(
        {
            "tracking_enabled": (settings.MATOMO_TRACKING and server_url and site_id),
            "matomo_site_id": site_id,
            "matomo_server_url": server_url,
            "matomo_image_tracker_url": image_tracker(server_url, site_id, vid),
        }
    )

    additional_site_id = settings.MATOMO_ADDITIONAL_SITE_ID
    if type(additional_site_id) is int and additional_site_id > 0:
        context.update(
            {
                "matomo_additional_site_id": additional_site_id,
                "matomo_additional_image_tracker_url": image_tracker(
                    server_url, additional_site_id, vid
                ),
            }
        )

    return context


def visitor_id(request):
    session = request.session

    if not session.get(VISITOR_ID_KEY):
        session[VISITOR_ID_KEY] = generate_random_id()

    return session[VISITOR_ID_KEY]


def generate_random_id():
    return sha1(
        "".join(
            [
                datetime.now().isoformat(),
                str(uuid4()),
            ]
        ).encode("utf-8")
    ).hexdigest()[0:16]


def image_tracker(server_url, site_id, vid):
    return f"{server_url}matomo.php?idsite={site_id}&rec=1&_id={vid}"
