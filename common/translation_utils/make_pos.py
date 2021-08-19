import polib
import csv
import copy
import os

class Translation(object):
    pass

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


sheet = open("translations.csv", newline='')
reader = csv.reader(sheet)

translations = []
for i, row in enumerate(reader):
    if i == 0:
        for lang in row[4:]:
            translation = Translation()
            po = polib.POFile()
            po.metadata = copy.deepcopy(po_metadata_template)
            translation.pofile = po
            translations.append(translation)
    for translation, phrase in zip(translations, row[4:]):
        phrase_eng = row[3]
        if row[0] == 'Section':
            continue
        if row[0] == 'll':
            translation.path = "locale/{}/LC_MESSAGES/".format(phrase)
        if row[0] == 'Language':
            translation.pofile.metadata["Laguage"] = phrase
        if row[0] == '':
            entry = polib.POEntry(
                msgid=phrase_eng,
                msgstr=phrase,
            )
            translation.pofile.append(entry)
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

sheet.close()

for translation in translations:
    os.makedirs(translation.path, exist_ok=True)
    filename = os.path.join(translation.path, "django.po")
    translation.pofile.save(filename)
