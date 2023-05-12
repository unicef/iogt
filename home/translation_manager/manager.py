import os
import polib

import translation_manager.manager
from translation_manager.models import TranslationEntry
from translation_manager.utils import (
    get_lang_from_dirname,
    get_locale_parent_dirname,
    get_relative_locale_path,
)


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

