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


sheet = open("translation_status.csv", newline='')
reader = csv.reader(sheet)

sheet2 = open("translations.csv", newline='')
data = list(csv.reader(sheet2))
phrases = set(r[1] for r in data)
processed_phrases = set()

# TODO: Log out -> Sign Out

entries = []
for i, row in enumerate(reader):
    if i == 0:
        translation = Translation()
        po = polib.POFile()
        po.metadata = copy.deepcopy(po_metadata_template)
        po.metadata["Language"] = "Testing"
        continue
    plural = False
    phrase = row[0]
    if phrase in processed_phrases:
        continue
    processed_phrases.add(phrase)
    if phrase[:12] == "msgid_plural":
        phrase = phrase[14:-1]
        plural = True
    context = row[1]
    if context == "BE":
        trans = f"([BE]-{phrase})"
    elif context == "remove":
        trans = f"([remove]-{phrase})"
    elif context == "not needed":
        trans = f"([not-needed]-{phrase})"
    else:
        status = row[2]
        if status == 'i' or status == 'yy':
            alt = row[3]
            if alt in phrases:
                if status == 'i':
                    trans = f"([has improv translation]-{phrase})"
                if status == 'yy':
                    trans = f"([has translation]-{phrase})"
            else:
                print("i or yy phrase not in sheet: ", row)
                continue
        elif status == 'y':
            if phrase in phrases:
                trans = f"([has translation]-{phrase})"
            else:
                print("y phrase not in sheet: ", row)
                continue
        elif status == 'n' or status == 'nn':
            trans = f"([needs translation]-{phrase})"
        # elif status == '?':
        else:
            print("Weird status: ", row)

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
        entries.append(entry)

for entry in entries:
    po.append(entry)

sheet.close()

po.save("test-out.po")
