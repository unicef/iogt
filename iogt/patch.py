from translation_manager import utils


def get_dirname_from_lang(lang):
    "Converts lang in format en-gb to format en_GB"

    return lang


def get_lang_from_dirname(dirname):
    "Converts lang in format en_GB to format en-gb"

    return dirname


utils.get_dirname_from_lang = get_dirname_from_lang
utils.get_lang_from_dirname = get_lang_from_dirname


def store_to_db(self, pofile, locale, store_translations=False):
    import os
    import polib

    from translation_manager.models import TranslationEntry
    from translation_manager.utils import get_relative_locale_path, get_locale_parent_dirname

    language = get_lang_from_dirname(locale)
    domain = os.path.splitext(os.path.basename(pofile))[0]
    messages = polib.pofile(pofile)
    translations = TranslationEntry.objects.filter(language=language)

    tdict = {}
    for t in translations:
        if t.original not in tdict:
            tdict.update({t.original: {}})
        tdict[t.original][t.language] = t.translation

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
        t, created = TranslationEntry.objects.update_or_create(
            original=m.msgid,
            language=language,
            locale_path=locale_path,
            domain=domain,
            defaults={
                "occurrences": "\n".join(occs),
                "translation": translation,
                "locale_parent_dir": locale_dir_name,
                "is_published": True,
            }
        )

        if locale_path not in self.tors:
            self.tors[locale_path] = {}
        if language not in self.tors[locale_path]:
            self.tors[locale_path][language] = {}
        if domain not in self.tors[locale_path][language]:
            self.tors[locale_path][language][domain] = []
        self.tors[locale_path][language][domain].append(t.original)


def patch_store_to_db():
    from translation_manager.manager import Manager

    Manager.store_to_db = store_to_db
