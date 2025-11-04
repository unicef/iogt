from uuid import uuid4
from hashlib import sha1
from datetime import datetime
from urllib.parse import urlencode

from django import template
from django.conf import settings
import random

import re
from urllib.parse import urlparse

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

    #new params
    action_name = get_page_title(context['request'])
    full_url = context['request'].build_absolute_uri()
    rand_value = str(random.randint(0, 999999))  # Random value to prevent caching
    apiv = "1"  # API version

    user_id = None
    if context.get("request") and context["request"].user.is_authenticated:
        user_id = context["request"].user.email

    dict_params = {
        "idsite": site_id,
        "rec": "1",
        "action_name": action_name,
        "url": full_url,
        "_id": vid,
        "rand": rand_value,
        "apiv": apiv,
    }

    if user_id:
        dict_params["uid"] = user_id
        
    # --- NEW: attach the same custom dimension for pixel hits ---
    dim_id = getattr(settings, "MATOMO_CANONICAL_DIMENSION_ID", None)
    if dim_id:
        all_lang_url = canonical_all_lang_url(full_url)
        dict_params[f"dimension{dim_id}"] = all_lang_url

    context.update(
        {
            "tracking_enabled": enabled,
            "matomo_site_id": site_id,
            "matomo_server_url": server_url,
            "matomo_image_tracker_url": image_tracker(server_url, site_id, vid, dict_params=dict_params),
            "page_title": get_page_title(context["request"]),
            "visitor_id": vid,
            "user_id": user_id,
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


def image_tracker(server_url, site_id, vid=None, action_name=None, full_url=None, dict_params=None):
    # Base parameters
    params = {
        "idsite": site_id,
        "rec": "1",
        "apiv": "1",  # API version
    }
    # Add optional parameters
    if vid:
        params["_id"] = vid
    if action_name:
        params["action_name"] = action_name
    if full_url:
        params["url"] = full_url
    # Add a random value to prevent caching
    params["rand"] = str(random.randint(0, 999999))

    if dict_params:
        params.update(dict_params)

    # Build the URL with query parameters
    return f"{server_url}matomo.php?{urlencode(params)}"

def get_page_title(request):
    if hasattr(request, 'page') and request.page:
        return request.page.title
    return "Untitled Page"


LANG_RE = re.compile(r'^([a-z]{2,3})([-_][a-z]{2})?$', re.IGNORECASE)

def canonicalize_path(path: str) -> str:
    parts = path.split('/')
    if len(parts) > 1 and LANG_RE.match(parts[1]) and parts[1].lower() != 'all_lang':
        parts[1] = 'all_lang'
        return '/'.join(parts)
    return path

def canonical_all_lang_url(full_url: str) -> str:
    parsed = urlparse(full_url)
    new_path = canonicalize_path(parsed.path)
    # keep query/fragment
    return f"{parsed.scheme}://{parsed.netloc}{new_path}{('?' + parsed.query) if parsed.query else ''}{('#' + parsed.fragment) if parsed.fragment else ''}"
