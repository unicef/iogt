import csv
import polib

class Translation:
    def __init__(self, row):
        self.phrase = row[3]
        self.bad_locales = row[1].split(',')
        self.bad_source_phrase = row[2]
        self.tag = row[0]
        self.translations = row[3:]

    def needs_improvement(self):
        return self.bad_source_phrase != ''

    def is_phrase(row):
        return row[0] in ['', 'sg', 'pl']


def lookup_status(msg, replacement_strings=[]):
    status = 'needs translation'
    if msg in translations:
        tr = translations[msg]
        if tr.needs_improvement():
            status = 'has improv-translation'
        else:
            status = 'has translation'
    for replacement_string in replacement_strings:
        if replacement_string:
            if replacement_string in translations:
                tr = translations[replacement_string]
                status = 'TODO'
            else:
                print(f'Warning: Replacement string "{replacement_string}" for message "{msg}" not in translations.')
    return status


def process_message(msg):
    po_msgs.add(msg)
    if msg not in logged_phrases:
        status = lookup_status(msg)
        status_sheet.append([msg, '', status, '', ''])
    else:
        status_row = status_sheet[logged_phrases[msg]]
        context = status_row[1]
        replacement_strings = status_row[4].split('|')
        if context in ['BE', 'not needed']:
            status_row[2] = 'not needed'
        elif context == 'remove':
            status_row[2] = 'TODO'
        else:
            status_row[2] = lookup_status(msg, replacement_strings)


po = polib.pofile('../../locale/xy/LC_MESSAGES/django.po')

sheet = open("translation_status.csv", newline='')
status_sheet = list(csv.reader(sheet))
logged_phrases = {status_sheet[i][0] : i for i in range(1, len(status_sheet))}

sheet2 = open("translations.csv", newline='')
translations = {r[3] : Translation(r) for r in list(csv.reader(sheet2)) if Translation.is_phrase(r)}
po_msgs = set()

for entry in po:
    if entry.obsolete:
        continue
    process_message(entry.msgid)
    if entry.msgid_plural:
        process_message(entry.msgid_plural)

for status_row in status_sheet[1:]:
    if status_row[0] not in po_msgs and status_row[1] != 'django':
        status_row[2] = 'unused'


out_sheet = open("translation_status.csv", 'w', newline='')
writer = csv.writer(out_sheet)
writer.writerows(status_sheet)
