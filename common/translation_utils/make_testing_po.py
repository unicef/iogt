import polib
import csv
import copy
import os

def make_testing_po_run():

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


    sheet = open("common/translation_utils/translation_status.csv", newline='')
    reader = csv.reader(sheet)

    sheet2 = open("common/translation_utils/translations.csv", newline='')
    data = list(csv.reader(sheet2))
    all_phrases = {r[3] : r for r in data}
    processed_phrases = set()

    entries = []
    entriesjs = []
    for i, row in enumerate(reader):
        if i == 0:
            po = polib.POFile()
            po.metadata = copy.deepcopy(po_metadata_template)
            po.metadata["Language"] = "Testing"
            pojs = polib.POFile()
            pojs.metadata = copy.deepcopy(po_metadata_template)
            pojs.metadata["Language"] = "Testing"
            continue
        plural = False
        phrase = row[0]
        if phrase in processed_phrases:
            continue
        processed_phrases.add(phrase)
        if phrase in all_phrases and all_phrases[phrase][0] == 'pl':
            plural = True
        tag = row[4].replace(' ', '-')
        trans = f"([{tag}]-{phrase})"

        if plural:
            entry = entries[-1]
            new_entry = polib.POEntry(
                msgid=entry.msgid,
                msgid_plural=phrase,
                msgstr_plural={0: entry.msgstr, 1: trans}
            )
            entries[-1] = new_entry
        else:
            entry = polib.POEntry(
                msgid=phrase,
                msgstr=trans,
            )
            if row[3] == 'js':
                entriesjs.append(entry)
            else:
                entries.append(entry)

    for entry in entries:
        po.append(entry)
    for entry in entriesjs:
        pojs.append(entry)

    sheet.close()

    os.makedirs("locale/xy/LC_MESSAGES/", exist_ok=True)
    po.save("locale/xy/LC_MESSAGES/django.po")
    pojs.save("locale/xy/LC_MESSAGES/djangojs.po")
