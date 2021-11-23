import polib
import csv
import copy
import os

class Translation(object):
    pass

def make_translation():
        translation = Translation()
        po = polib.POFile()
        po.metadata = copy.deepcopy(po_metadata_template)
        translation.pofile = po
        return translation

po_metadata_template = {
    "Report-Msgid-Bugs-To": "",
    "POT-Creation-Date": "2021-07-31 09:38+0000",
    "PO-Revision-Date": "2021-07-31 09:38+0000",
    "Last-Translator": "FULL NAME <EMAIL@ADDRESS>",
    "Language-Team": "LANGUAGE <LL@li.org>",
    "Language": "",
    "MIME-Version": "1.0",
    "Content-Type": "text/plain; charset=UTF-8",
    "Content-Transfer-Encoding": "8bit",
    "Project-Id-Version": "PACKAGE VERSION",
    "Plural-Forms": "nplurals=2; plural=(n > 1);",
}

sheet0 = open("translation_status.csv", newline='')
status_data = list(csv.reader(sheet0))
js_phrases = set()
for row in status_data:
    if row[3] == 'js':
        js_phrases.add(row[0])

processed_phrases = set()


sheet = open("translations.csv", newline='')
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
    translation_list = translations
    if phrase_eng in js_phrases:
        translation_list = translationsjs
    for translation, phrase in zip(translation_list, row[4:]):
        if row[0] == 'Section':
            continue
        if row[0] == '':
            entry = polib.POEntry(
                msgid=phrase_eng,
                msgstr=phrase,
            )
            translation.pofile.append(entry)
            processed_phrases.add(phrase_eng)
        if row[0] == 'sg':
            translation.sg_buffer = phrase
            translation.sg_buffer_eng = phrase_eng
        if row[0] == 'pl':
            if not translation.sg_buffer:
                print("Warning: Row {} has no matching singular.".format(i))
                continue
            entry = polib.POEntry(
                msgid=translation.sg_buffer_eng,
                msgid_plural=phrase_eng,
                msgstr_plural={0: translation.sg_buffer, 1: phrase}
            )
            translation.pofile.append(entry)
            processed_phrases.add(translation.sg_buffer_eng)
            processed_phrases.add(phrase_eng)

sheet.close()

translatable_strings = []
# Update with translations that we need but don't have
for i, row in enumerate(status_data):
    phrase = row[0]
    if i == 0:
        continue
    if row[2] == 'translate' and row[4] != 'unused' and phrase not in processed_phrases:
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
        if row[4] == 'needs translation':
            translatable_strings.append(phrase)

# Write output
for translation in translations:
    os.makedirs(translation.path, exist_ok=True)
    filename = os.path.join(translation.path, "django.po")
    translation.pofile.save(filename)
for translation in translationsjs:
    filename = os.path.join(translation.path, "djangojs.po")
    translation.pofile.save(filename)

with open("translatable_strings.py", 'w') as f:
    f.write('translatable_strings = ' + str(translatable_strings))
