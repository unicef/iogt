import polib
import csv
import copy
import os
from common.translation_utils.po_template import get_po_metadata_template

class Translation(object):
    pass

def make_translation():

    po_metadata_template = get_po_metadata_template()

    translation = Translation()
    po = polib.POFile()
    po.metadata = copy.deepcopy(po_metadata_template)
    translation.pofile = po
    return translation

def make_pos_run():

    sheet0 = open("common/translation_utils/translation_status.csv", newline='')
    status_data = list(csv.reader(sheet0))
    js_phrases = set()
    used_phrases = set()
    used_phrases_map = {}
    for row in status_data:
        if row[3] == 'js':
            js_phrases.add(row[0])
            js_phrases.add(row[0].strip().lower())
        if row[2] not in ['remove', 'not needed'] and row[4] != 'unused':
            used_phrases.add(row[0])
            norm = row[0].strip().lower()
            if norm not in used_phrases_map:
                used_phrases_map[norm] = row[0]

    processed_phrases = set()


    sheet = open("common/translation_utils/translations.csv", newline='')
    reader = csv.reader(sheet)

    translations = []
    translationsjs = []
    # Compile PO files from official translation sheet
    for i, row in enumerate(reader):
        if i == 0:
            for lang in row[4:]:
                translations.append(make_translation())
                translationsjs.append(make_translation())
        if row[0] == 'll':
            for translation, phrase in zip(translations, row[4:]):
                translation.path = "locale/{}/LC_MESSAGES/".format(phrase)
            for translation, phrase in zip(translationsjs, row[4:]):
                translation.path = "locale/{}/LC_MESSAGES/".format(phrase)
        if row[0] == 'Language':
            for translation, phrase in zip(translations, row[4:]):
                translation.path = "locale/{}/LC_MESSAGES/".format(phrase)
            for translation, phrase in zip(translationsjs, row[4:]):
                translation.pofile.metadata["Language"] = phrase
                translation.path = "locale/{}/LC_MESSAGES/".format(phrase)

        phrase_eng = row[3]
        canonical_phrase = None
        if phrase_eng in used_phrases:
            canonical_phrase = phrase_eng
        else:
            norm = phrase_eng.strip().lower()
            if norm in used_phrases_map:
                candidate = used_phrases_map[norm]
                if candidate not in processed_phrases:
                    canonical_phrase = candidate

        if not canonical_phrase or canonical_phrase in processed_phrases:
            continue

        translation_list = translations
        if canonical_phrase in js_phrases or phrase_eng in js_phrases:
            translation_list = translationsjs

        for translation, phrase in zip(translation_list, row[4:]):
            if row[0] == 'Section':
                continue
            if row[0] == '':
                entry = polib.POEntry(
                    msgid=canonical_phrase,
                    msgstr=phrase,
                )
                translation.pofile.append(entry)
                processed_phrases.add(canonical_phrase)
            if row[0] == 'sg':
                translation.sg_buffer = phrase
                translation.sg_buffer_eng = canonical_phrase
            if row[0] == 'pl':
                if not hasattr(translation, "sg_buffer"):
                    print("Warning: Row {} has no matching singular.".format(i))
                    continue
                entry = polib.POEntry(
                    msgid=translation.sg_buffer_eng,
                    msgid_plural=canonical_phrase,
                    msgstr_plural={0: translation.sg_buffer, 1: phrase}
                )
                translation.pofile.append(entry)
                processed_phrases.add(translation.sg_buffer_eng)
                processed_phrases.add(canonical_phrase)

    sheet.close()

    translatable_strings = []
    # Update with translations that we need but don't have
    for i, row in enumerate(status_data):
        phrase = row[0]
        if i == 0:
            continue
        if row[2] not in ['remove', 'not needed'] and row[4] != 'unused':
            if phrase not in processed_phrases:
                assert not row[4].startswith('has translation')
                translation_list = translations
                if row[3] == 'js':
                    translation_list = translationsjs
                for translation in translation_list:
                    entry = polib.POEntry(
                        msgid=phrase,
                        msgstr='',
                    )
                    translation.pofile.append(entry)                
                processed_phrases.add(phrase)

            if row[4] == 'needs translation' or row[4] == 'has partial translation':
                translatable_strings.append(phrase)

    # Write output
    for translation in translations:
        os.makedirs(translation.path, exist_ok=True)
        filename = os.path.join(translation.path, "django.po")
        translation.pofile.save(filename)
    for translation in translationsjs:
        filename = os.path.join(translation.path, "djangojs.po")
        translation.pofile.save(filename)

    with open("home/translatable_strings.py", 'w') as f:
        content = ",\n    ".join(e.__repr__() for e in translatable_strings)
        f.write(f'translatable_strings = [\n    {content}\n]')
