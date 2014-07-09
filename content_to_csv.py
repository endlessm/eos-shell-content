#!/usr/bin/python3
# Note: use python3 for direct support of utf-8 strings

# This script requires python3 polib
# (sudo apt-get install python3-polib)

# To use this script, export spreadsheet from master content doc
# and save in this folder as content.csv
# Run this script to process and update content.csv
# Note that the original row order is maintained,
# and any new apps added are at the bottom of content.csv
# Add and commit any changes to git
# Merge changes into master content doc

import csv
import json
import os
import polib

CONTENT_JSON = 'content/Default/apps/content.json'
CONTENT_CSV = 'content.csv'
PO_DIR = 'po'
LANGS = {'en': 'GLOBAL',
         'es': 'SPANISH',
         'pt': 'PORTUGUESE'}

if __name__ == '__main__':

    # Load the content json data from file
    with open(CONTENT_JSON) as json_file:
        json_data = json.load(json_file)

    # Open the input csv reader
    with open(CONTENT_CSV, newline='') as in_file:
        in_lines = in_file.readlines()
    csv_reader = csv.reader(in_lines)

    # Open the output csv writer
    with open(CONTENT_CSV, 'w', newline='') as out_file:
        csv_writer = csv.writer(out_file)

        # Read and parse the two-row header
        header1 = csv_reader.__next__()
        header2 = csv_reader.__next__()
        lang_idx = {}
        for lang in LANGS:
            lang_idx[lang] = header1.index(LANGS[lang])
        appid_idx = header2.index('App Id')
        origname_idx = header2.index('Original Name')
        num_cols = len(header2)
        empty_row = [''] * num_cols

        # Open po files
        po = {}
        for lang in LANGS:
            if lang != 'en':
                po_file = os.path.join(PO_DIR, lang + '.po')
                po[lang] = polib.pofile(po_file)

        def populate_row(csv_row, json_row):
            csv_row[appid_idx] = json_row['application-id']
            en_title = json_row['title']
            en_subtitle = json_row['subtitle']
            en_description = json_row['description']

            def translate(lang, val):
                entry = po[lang].find(val)
                if entry:
                    translation = entry.msgstr
                else:
                    translation = ''
                return translation

            for lang in LANGS:
                title_idx = lang_idx[lang]
                subtitle_idx = lang_idx[lang] + 1
                description_idx = lang_idx[lang] + 2
                if (lang == 'en'):
                    title = en_title
                    subtitle = en_subtitle
                    description = en_description
                else:
                    title = translate(lang, en_title)
                    subtitle = translate(lang, en_subtitle)
                    description = translate(lang, en_description)
                csv_row[title_idx] = title
                csv_row[subtitle_idx] = subtitle
                csv_row[description_idx] = description

        # Write the two-row header
        csv_writer.writerow(header1)
        csv_writer.writerow(header2)

        # Process each row of the input csv
        for csv_row in csv_reader:
            app_id = csv_row[appid_idx]
            if app_id:
                # Csv already has app id: search for it in json
                for json_row in json_data:
                    if json_row['application-id'] == app_id:
                        # Found a match in json
                        break
                else:
                    # No match in json: leave the csv alone
                    json_row = None
            else:
                # Csv does not have app id yet: try searching by original name
                orig_name = csv_row[origname_idx]
                for json_row in json_data:
                    if json_row['title'] == orig_name:
                        # Found a matching name
                        break
                else:
                    # No matching name: leave the csv alone
                    json_row = None

            # If matching json content found, use it to fill part of the csv,
            # and mark the json data as having been used
            if json_row:
                populate_row(csv_row, json_row)
                json_row['used'] = True

            # Write the possibly modified csv row
            csv_writer.writerow(csv_row)

        # Append any additional content from json that is not yet in csv
        for json_row in json_data:
            if not 'used' in json_row:
                csv_row = empty_row
                populate_row(csv_row, json_row)
                csv_writer.writerow(csv_row)
