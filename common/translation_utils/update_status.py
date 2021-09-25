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
            status = 'has translation (improvised)'
        else:
            status = 'has translation'
    else:
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
        status_sheet.append([msg, '', '', '', status, '', '', ''])
    else:
        status_row = status_sheet[logged_phrases[msg]]
        tag = status_row[2]
        replacement_strings = status_row[6].split('|')
        if tag == 'not needed':
            status_row[4] = 'not needed'
        elif tag == 'remove':
            status_row[4] = 'TODO'
        else:
            status_row[4] = lookup_status(msg, replacement_strings)
            if status_row[4] == 'needs translation' and status_row[3] == 'django':
                status_row[4] = 'needs translation (partial)'

po = polib.pofile('../../locale/xy/LC_MESSAGES/django.po')

sheet = open("translation_status.csv", newline='')
status_sheet = list(csv.reader(sheet))
logged_phrases = {status_sheet[i][0] : i for i in range(1, len(status_sheet))}

sheet2 = open("translations.csv", newline='')
translations = {r[3] : Translation(r) for r in list(csv.reader(sheet2)) if Translation.is_phrase(r)}
po_msgs = set()

# process those rows that are in the PO file
for entry in po:
    if entry.obsolete:
        continue
    process_message(entry.msgid)
    if entry.msgid_plural:
        process_message(entry.msgid_plural)

# Process the remaining rows
for status_row in status_sheet[1:]:
    if status_row[0] not in po_msgs:
        if status_row[3] == 'django':
            process_message(status_row[0])
        else:
            status_row[4] = 'unused'


out_sheet = open("translation_status.csv", 'w', newline='')
writer = csv.writer(out_sheet)
writer.writerows(status_sheet)
