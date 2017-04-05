#!/usr/bin/env python3

# Handle translations in bundle/translations.json

import json
import os

srcdir = os.path.dirname(os.path.realpath(__file__))
CONTENT_JSON_FILE = os.path.join(srcdir,
                                 'content/Default/apps/content.json')
TRANSLATIONS_JSON_FILE = os.path.join(srcdir, 'bundle/translations.json')

def merge_translation_info(content):
    """Merge translations.json information to content data"""
    with open(TRANSLATIONS_JSON_FILE) as f:
        trans_data = json.load(f)

    for app_data in content:
        app_id = app_data['application-id']

        # Merge in translation information if available
        translation_id = translation_type = None
        if app_id in trans_data:
            translation_id = trans_data[app_id].get('translation_id')
            translation_type = trans_data[app_id].get('translation_type')
        app_data['translation_id'] = translation_id
        app_data['translation_type'] = translation_type

def main():
    from argparse import ArgumentParser

    aparser = ArgumentParser(
        description='Merge translations.json data into content.json',
    )
    args = aparser.parse_args()

    with open(CONTENT_JSON_FILE) as f:
        content = json.load(f)
    merge_translation_info(content)
    with open(CONTENT_JSON_FILE, 'w') as f:
        json.dump(content, f, indent=2, sort_keys=True)

if __name__ == '__main__':
    main()
