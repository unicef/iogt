# core/templatetags/track.py
from django import template
from wagtail.models import Locale

register = template.Library()

@register.simple_tag(takes_context=True)
def matomo_all_lang_vars(context, page):
    """
    Returns a dict with:
    key   -> stable ID for this logical page (translation_key)
    title -> human label from default-locale version
    url   -> synthetic canonical URL, independent of actual front-end URL
    """
    default_locale = Locale.get_default()

    # Use default-locale translation as canonical name, if exists
    try:
        canonical_page = page.get_translation(default_locale)
    except Exception:
        canonical_page = page  # fallback

    key = str(page.translation_key)  # same for all language versions
    title = canonical_page.title

    # Synthetic URL *not* based on the real URL
    # All translations of the same article will share this:
    #   /all_lang/<translation_key>/
    synthetic_url = f"/all_lang/{key}/"

    return {
        "key": key,
        "title": title,
        "url": synthetic_url,
    }
