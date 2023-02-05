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

    lookup = (self.filter_expression.var.literal or 
                self.filter_expression.var._resolve_lookup(context))

    try:
        translation_entry = cache.get(f'{globals_.locale.language_code}_translation_map')[
            (lookup, globals_.locale.language_code)]
    except (KeyError, TypeError):
        translation_entry = None

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


def _translate_block_node_render(self, context, nested=False):
    from django.core.cache import cache
    from django.template import TemplateSyntaxError
    from django.template.base import render_value_in_context
    from django.utils import translation

    if self.message_context:
        message_context = self.message_context.resolve(context)
    else:
        message_context = None
    # Update() works like a push(), so corresponding context.pop() is at
    # the end of function
    context.update({var: val.resolve(context) for var, val in self.extra_context.items()})
    singular, vars = self.render_token_list(self.singular)
    if self.plural and self.countervar and self.counter:
        count = self.counter.resolve(context)
        context[self.countervar] = count
        plural, plural_vars = self.render_token_list(self.plural)
        if message_context:
            result = translation.npgettext(message_context, singular,
                                           plural, count)
        else:
            result = translation.ngettext(singular, plural, count)
        vars.extend(plural_vars)
    else:
        if message_context:
            result = translation.pgettext(message_context, singular)
        else:
            result = translation.gettext(singular)
    default_value = context.template.engine.string_if_invalid

    try:
        translation_entry = cache.get(f'{globals_.locale.language_code}_translation_map')[
            (singular, globals_.locale.language_code)]
    except (KeyError, TypeError):
        translation_entry = None

    if translation_entry and translation_entry.translation:
        result = translation_entry.translation

    def render_value(key):
        if key in context:
            val = context[key]
        else:
            val = default_value % key if '%s' in default_value else default_value
        return render_value_in_context(val, context)

    data = {v: render_value(v) for v in vars}
    context.pop()
    try:
        result = result % data
    except (KeyError, ValueError):
        if nested:
            # Either string is malformed, or it's a bug
            raise TemplateSyntaxError(
                '%r is unable to format string returned by gettext: %r '
                'using %r' % (self.tag_name, result, data)
            )
        with translation.override(None):
            result = self.render(context, nested=True)
    if self.asvar:
        context[self.asvar] = result
        return ''
    else:
        return result


utils.get_dirname_from_lang = get_dirname_from_lang
utils.get_lang_from_dirname = get_lang_from_dirname
i18n.TranslateNode.render = _translate_node_render
i18n.BlockTranslateNode.render = _translate_block_node_render


def store_to_db(self, pofile, locale, store_translations=False):
    import os
    import polib

    from translation_manager.models import TranslationEntry
    from translation_manager.utils import get_relative_locale_path, get_locale_parent_dirname

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

    TranslationEntry.objects.filter(id__in=[t.id for t in to_delete]).delete()
    TranslationEntry.objects.bulk_create(to_create)


def patch_store_to_db():
    from translation_manager.manager import Manager
    Manager.store_to_db = store_to_db
