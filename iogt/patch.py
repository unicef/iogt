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


    translations_to_keep = []
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

        if not m.msgstr:
            t = TranslationEntry.objects.filter(
                original=m.msgid, language=language, locale_path=locale_path, domain=domain
            ).first()
            if t:
                if t.translation:
                    translations_to_keep.append(m.msgid)
                    continue

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

        translations_to_keep.append(m.msgid)

        if locale_path not in self.tors:
            self.tors[locale_path] = {}
        if language not in self.tors[locale_path]:
            self.tors[locale_path][language] = {}
        if domain not in self.tors[locale_path][language]:
            self.tors[locale_path][language][domain] = []
        self.tors[locale_path][language][domain].append(t.original)

    return translations_to_keep


def update_po_from_db(self, lang):
    import logging
    import os
    from datetime import datetime

    import polib
    from django.conf import settings
    from translation_manager.models import TranslationEntry
    from translation_manager.settings import get_settings

    logger = logging.getLogger('translation_manager')


    translations = TranslationEntry.objects.filter(
        language=lang,
        is_published=True
    ).order_by("original")

    locale_params = TranslationEntry.objects.filter(is_published=True).order_by('locale_path', 'domain')

    forced_locale_paths = get_settings('TRANSLATIONS_UPDATE_FORCED_LOCALE_PATHS')
    if forced_locale_paths:
        translations = translations.filter(locale_path__in=forced_locale_paths)
        locale_params = locale_params.filter(locale_path__in=forced_locale_paths)

    locale_params = locale_params.values_list('locale_path', 'domain')
    locale_params = list(set(locale_params))

    for locale_path, domain in locale_params:
        lang_dir_path = os.path.abspath(
            os.path.join(get_settings('TRANSLATIONS_BASE_DIR'), locale_path, get_dirname_from_lang(lang)))
        if not os.path.isdir(lang_dir_path):
            os.mkdir(lang_dir_path)
            os.mkdir(os.path.join(lang_dir_path, 'LC_MESSAGES'))

        pofile_path = os.path.join(get_settings('TRANSLATIONS_BASE_DIR'), locale_path, get_dirname_from_lang(lang),
                                   'LC_MESSAGES',
                                           "%s.po" % domain)
        mofile_path = os.path.join(get_settings('TRANSLATIONS_BASE_DIR'), locale_path, get_dirname_from_lang(lang),
                                   'LC_MESSAGES',
                                           "%s.mo" % domain)

        if not os.path.exists(pofile_path):
            logger.debug("Po file '{}' does't exists, it will be created".format(pofile_path))

        now = datetime.now()
        pofile = polib.POFile()
        pofile.metadata = {
            'Project-Id-Version': '0.1',
            'Report-Msgid-Bugs-To': '%s' % settings.DEFAULT_FROM_EMAIL,
            'POT-Creation-Date': now.strftime("%Y-%m-%d %H:%M:%S"),
            'PO-Revision-Date': now.strftime("%Y-%m-%d %H:%M:%S"),
            'Last-Translator': 'Server <%s>' % settings.SERVER_EMAIL,
            'Language-Team': 'English <%s>' % settings.DEFAULT_FROM_EMAIL,
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }

        for translation in translations.filter(locale_path=locale_path, domain=domain):
            entry = polib.POEntry(
                flags=['fuzzy'],
                msgid=translation.original,
                msgstr=translation.translation,
                occurrences=[occ.split(":") for occ in translation.occurrences.split()]
            )
            pofile.append(entry)

        pofile.save(pofile_path)
        pofile.save_as_mofile(mofile_path)


def load_data_from_po(self):
    import os
    from glob import glob

    from django.conf import settings
    from django.db.models import Q
    from translation_manager.models import TranslationEntry

    translations_to_keep = []
    for lang, lang_name in settings.LANGUAGES:
        for path in settings.LOCALE_PATHS:
            locale = get_dirname_from_lang(lang)
            po_pattern = os.path.join(path, locale, "LC_MESSAGES", "*.po")
            for pofile in glob(po_pattern):
                translations_to_keep += self.store_to_db(pofile=pofile, locale=locale, store_translations=True)

    self.postprocess()
    TranslationEntry.objects.exclude(Q(Q(original__in=translations_to_keep) | ~Q(translation=''))).delete()
    TranslationEntry.objects.filter(Q(Q(original__in=translations_to_keep) | ~Q(translation=''))).update(is_published=True)


def patch_store_to_db():
    from translation_manager.manager import Manager

    Manager.store_to_db = store_to_db
    Manager.load_data_from_po = load_data_from_po
    Manager.update_po_from_db = update_po_from_db
