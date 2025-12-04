# home/templatetags/offline_tags.py
from django import template
from wagtail.rich_text import RichText  # safe import if present
try:
    # Wagtail 5/6/7 StreamField
    from wagtail.fields import StreamValue
except Exception:
    from wagtail.core.fields import StreamValue  # fallback for older

register = template.Library()

DOWNLOAD_BLOCK_NAMES = {
    # add/adjust to match your project
    "download",
    "offline_download",
    "download_block",
    "offline_app",
    "download_app",
    "block_download",  # your HTML shows <div class="block-download"> (hyphen vs underscore)
}

STREAMFIELD_NAMES_TO_SCAN = [
    "body", "content", "main", "stream", "article_body", "sections",
]

def _stream_has_download_block(value):
    """Recursively scan StreamField for a known download/offline block type."""
    if not isinstance(value, StreamValue):
        return False

    for child in value:
        # direct match on block type
        if getattr(child, "block_type", None) in DOWNLOAD_BLOCK_NAMES:
            return True

        # nested stream blocks (cards/structs)
        child_val = getattr(child, "value", None)

        # If nested is another StreamValue, recurse
        if isinstance(child_val, StreamValue) and _stream_has_download_block(child_val):
            return True

        # If it's a StructBlock with inner stream(s), walk its items
        if hasattr(child_val, "items"):
            for k, v in child_val.items():
                if isinstance(v, StreamValue) and _stream_has_download_block(v):
                    return True

    return False

@register.filter(name="is_downloadable")
def is_downloadable(page):
    """
    Returns True if this page contains the 'download/offline' content block
    (i.e., the page shows the 'Offline text'/'Available text' buttons).
    """
    sp = getattr(page, "specific", page)

    # 1) Prefer explicit boolean flags if your models have them
    for attr in ("enable_offline_download", "offline_download_enabled", "download_available"):
        if hasattr(sp, attr):
            val = getattr(sp, attr)
            if isinstance(val, bool):
                return val

    # 2) Otherwise detect presence of the block in common streamfields
    for field_name in STREAMFIELD_NAMES_TO_SCAN:
        if hasattr(sp, field_name):
            try:
                if _stream_has_download_block(getattr(sp, field_name)):
                    return True
            except Exception:
                pass

    return False
