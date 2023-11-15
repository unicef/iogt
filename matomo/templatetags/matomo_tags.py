from uuid import uuid4
from hashlib import sha1
from datetime import datetime

from django import template
from django.conf import settings


VISITOR_ID_KEY = "vid"
register = template.Library()


@register.inclusion_tag("matomo_tag_manager.html", takes_context=True)
def matomo_tag_manager(context, container_id=None):
    try:
        server_url = settings.MATOMO_SERVER_URL
    except AttributeError:
        server_url = None

    if server_url and container_id:
        context.update({"mtm_src": f"{server_url}js/container_{container_id}.js"})

    return context


@register.inclusion_tag("matomo_tracking_tags.html", takes_context=True)
def matomo_tracking_tags(context):
    enabled = is_enabled()

    if not enabled:
        return context.update({"tracking_enabled": enabled})

    server_url = settings.MATOMO_SERVER_URL
    site_id = settings.MATOMO_SITE_ID
    vid = create_visitor_id(context)

    context.update(
        {
            "tracking_enabled": enabled,
            "matomo_site_id": site_id,
            "matomo_server_url": server_url,
            "matomo_image_tracker_url": image_tracker(server_url, site_id, vid),
        }
    )
    context.update(additional_site_id(server_url, vid))

    return context


def is_enabled():
    try:
        return (
            settings.MATOMO_TRACKING
            and settings.MATOMO_SERVER_URL
            and settings.MATOMO_SITE_ID
        )
    except AttributeError:
        return False


def create_visitor_id(context):
    try:
        if settings.MATOMO_CREATE_VISITOR_ID:
            return visitor_id(context["request"])
    except AttributeError:
        return None


def additional_site_id(server_url, vid=None):
    try:
        site_id = settings.MATOMO_ADDITIONAL_SITE_ID
    except AttributeError:
        return {}

    if type(site_id) is int and site_id > 0:
        return {
            "matomo_additional_site_id": site_id,
            "matomo_additional_image_tracker_url": image_tracker(
                server_url, site_id, vid
            ),
        }
    else:
        return {}


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


def image_tracker(server_url, site_id, vid=None):
    url = f"{server_url}matomo.php?idsite={site_id}&rec=1"

    if vid:
        url += f"&_id={vid}"

    return url
