# core/templatetags/track.py
from django import template
from wagtail.models import Locale

register = template.Library()

@register.simple_tag(takes_context=True)
def matomo_all_lang_vars(context, page=None):
    """
    Returns a dict with:
    key   -> stable ID for this logical page (translation_key)
    title -> human label from default-locale version
    url   -> synthetic canonical URL, independent of actual front-end URL
    available -> boolean flag; False when we can't resolve a translation_key
    """
    request = context.get("request")

    # Try to recover a Page if caller didn’t pass one
    if page is None:
        page = context.get("page") or getattr(request, "page", None)

    # If still no page or it's not translatable, bail out safely
    translation_key = getattr(page, "translation_key", None)
    if not translation_key:
        return {"key": "", "title": "", "url": "", "available": False}

    # Resolve a nice title from default locale, falling back to current page
    try:
        default_locale = Locale.get_default()
    except Exception:
        default_locale = None

    try:
        canonical_page = page.get_translation(default_locale) if default_locale else page
    except Exception:
        canonical_page = page

    key = str(translation_key)
    title = getattr(canonical_page, "title", "") or ""
    synthetic_url = f"/all_lang/{key}/"

    return {"key": key, "title": title, "url": synthetic_url, "available": True}
