import os, uuid, threading
from collections import defaultdict
import polib
from django.conf import settings
from django.core.cache import cache

VERSION_KEY = "translations_version"
_sync_lock = threading.Lock()


def publish_translation_version():
    """Called ONLY from the save/delete signal (after commit)."""
    for lang, _ in settings.LANGUAGES:
        cache.delete(f"{lang}_translation_map")
    cache.set(VERSION_KEY, uuid.uuid4().hex, timeout=None)


def _po_path(entry):
    d = entry.locale_path
    if not os.path.isabs(d):
        d = os.path.join(settings.BASE_DIR, d)
    return os.path.join(d, entry.language, "LC_MESSAGES", f"{entry.domain}.po")


def sync_all_po_files():
    from translation_manager.models import TranslationEntry

    by_file = defaultdict(list)
    for e in TranslationEntry.objects.exclude(locale_path="").iterator():
        path = _po_path(e)
        if os.path.isfile(path):
            by_file[path].append(e)

    for path, entries in by_file.items():
        po = polib.pofile(path)
        changed = False
        for e in entries:
            new = e.translation or ""
            pe = po.find(e.original)
            if pe is None:
                po.append(polib.POEntry(msgid=e.original, msgstr=new))
                changed = True
            elif pe.msgstr != new:
                pe.msgstr = new
                changed = True
        if changed:
            po.save(path)
            po.save_as_mofile(os.path.splitext(path)[0] + ".mo")

    from django.utils.translation import trans_real
    trans_real._translations = {}


def check_translations():
    """Cheap on the hot path: one cache GET + one comparison."""
    import iogt.iogt_globals as globals_

    cache_ver = cache.get(VERSION_KEY)
    if cache_ver is None:
        cache.add(VERSION_KEY, uuid.uuid4().hex, timeout=None)  # atomic, first one wins
        cache_ver = cache.get(VERSION_KEY)

    if globals_.translations_version == cache_ver:
        return

    with _sync_lock:                      # one thread per process syncs
        if globals_.translations_version == cache_ver:
            return
        sync_all_po_files()               # no publishing here
        clear_translations_cache()         # local/wagtail cache only
        globals_.translations_version = cache_ver
        
def clear_translations_cache():
    """Clear this pod's translation maps and the wagtail page cache."""
    from wagtailcache.cache import clear_cache
    for lang, _ in settings.LANGUAGES:
        cache.delete(f"{lang}_translation_map")
    clear_cache()