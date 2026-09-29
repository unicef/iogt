import os
import polib

import translation_manager.manager
from translation_manager.models import TranslationEntry
from translation_manager.utils import (
    get_lang_from_dirname,
    get_locale_parent_dirname,
    get_relative_locale_path,
)
from django.conf import settings
from django.core.cache import cache


class IogtTranslationManager(translation_manager.manager.Manager):

    def store_to_db(self, pofile, locale, store_translations=False):
        language = get_lang_from_dirname(locale)
        domain = os.path.splitext(os.path.basename(pofile))[0]
        messages = polib.pofile(pofile)
        translations = TranslationEntry.objects.filter(language=language)

        tdict = {
            (t.original, t.language, t.domain): t
            for t in translations
        }

        to_create = []
        to_delete = []
        for m in messages:
            occs = []
            for occ in m.occurrences:
                path = ":".join(occ)
                occs.append(path)

            if store_translations:
                translation = m.msgstr
            else:
                translation = ""

            locale_path = get_relative_locale_path(pofile)

            if os.path.split(pofile)[-1] == 'angularjs.po':
                locale_dir_name = ''
            else:
                locale_dir_name = get_locale_parent_dirname(pofile)

            entry = tdict.get((m.msgid, language, domain))

            t = TranslationEntry(
                original=m.msgid,
                language=language,
                domain=domain,
                occurrences="\n".join(occs),
                translation=translation,
                locale_parent_dir=locale_dir_name,
                is_published=True,
                locale_path=locale_path,
            )

            if not entry:
                to_create.append(t)
            elif entry.translation == '' and entry.translation != translation:
                to_delete.append(entry)
                to_create.append(t)

            if locale_path not in self.tors:
                self.tors[locale_path] = {}
            if language not in self.tors[locale_path]:
                self.tors[locale_path][language] = {}
            if domain not in self.tors[locale_path][language]:
                self.tors[locale_path][language][domain] = []
            self.tors[locale_path][language][domain].append(t.original)

        TranslationEntry.objects.filter(
            id__in=[t.id for t in to_delete]
        ).delete()
        TranslationEntry.objects.bulk_create(to_create)
        cache.delete(f'{language}_translation_map')


def update_po_from_translation_entry(entry):
    # print("=== PO UPDATE START ===")
    # print("original:", repr(entry.original))
    # print("language:", entry.language)
    # print("domain:", repr(entry.domain))
    # print("locale_path from DB:", repr(entry.locale_path))
    # print("BASE_DIR:", settings.BASE_DIR)
    if not entry.locale_path:
        return
    locale_dir = entry.locale_path

    if not os.path.isabs(locale_dir):
        locale_dir = os.path.join(settings.BASE_DIR, locale_dir)

    pofile = os.path.join(
        locale_dir,
        entry.language,
        "LC_MESSAGES",
        f"{entry.domain}.po",
    )


    if not os.path.isfile(pofile):
        return

    try:
        po = polib.pofile(pofile)
        po_entry = po.find(entry.original)

        if po_entry is None:

            po_entry = polib.POEntry(
                msgid=entry.original,
                msgstr=entry.translation or "",
            )

            po.append(po_entry)

        else:

            po_entry.msgstr = entry.translation or ""

        po.save(pofile)


        mo_path = os.path.splitext(pofile)[0] + ".mo"

        po.save_as_mofile(mo_path)

        from django.utils.translation import trans_real

        trans_real._translations = {}

        # Clear custom translation cache
        cache.delete(f"{entry.language}_translation_map")


    except Exception as e:
        raise

