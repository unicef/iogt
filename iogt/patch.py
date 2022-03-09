from django.templatetags import i18n
from translation_manager import utils
import iogt.iogt_globals as globals_


def get_dirname_from_lang(lang):
    "Converts lang in format en-gb to format en_GB"

    return lang


def get_lang_from_dirname(dirname):
    "Converts lang in format en_GB to format en-gb"

    return dirname


def _translate_node_render(self, context):
    from django.template.base import render_value_in_context
    from django.utils.safestring import SafeData
    from django.utils.safestring import mark_safe
    from django.core.cache import cache

    translation_entry = cache.get('translation_map').translation_map.get(
        (self.filter_expression.var.literal, globals_.locale.language_code))
    if translation_entry and translation_entry.translation:
        return translation_entry.translation

    self.filter_expression.var.translate = not self.noop
    if self.message_context:
        self.filter_expression.var.message_context = (
            self.message_context.resolve(context))
    output = self.filter_expression.resolve(context)


    value = render_value_in_context(output, context)
    # Restore percent signs. Percent signs in template text are doubled
    # so they are not interpreted as string format flags.
    is_safe = isinstance(value, SafeData)
    value = value.replace('%%', '%')
    value = mark_safe(value) if is_safe else value
    if self.asvar:
        context[self.asvar] = value
        return ''
    else:
        return value


utils.get_dirname_from_lang = get_dirname_from_lang
utils.get_lang_from_dirname = get_lang_from_dirname
i18n.TranslateNode.render = _translate_node_render


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

        t = TranslationEntry.objects.filter(original=m.msgid, language=language, domain=domain).first()
        if t:
            if t.translation:
                translations_to_keep.append(m.msgid)
                continue

        t, created = TranslationEntry.objects.update_or_create(
            original=m.msgid,
            language=language,
            domain=domain,
            defaults={
                "occurrences": "\n".join(occs),
                "translation": translation,
                "locale_parent_dir": locale_dir_name,
                "is_published": True,
                "locale_path": locale_path,
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
