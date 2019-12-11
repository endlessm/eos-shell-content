#!/usr/bin/python3
#
# Copyright (C) 2017 Endless Mobile, Inc.
#
# Authors:
#  Joaquim Rocha <jrocha@endlessm.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import collections
import gi
gi.require_version('AppStreamGlib', '1.0')
from gi.repository import AppStreamGlib
from gi.repository import Gio
import glob
import json
import os
import polib
import re
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET

CMS_GS_BUCKET_URL = 'https://d3lapyynmdp1i9.cloudfront.net'
DEFAULT_HOMEPAGE = 'https://endlessm.com'
LOCALES_DIR = '/usr/share/locale/'
EOS_CONTENT_JSON = '/usr/share/eos-shell-content/content.json'

class NoMetadataException(Exception):
    def __init__(self, appid):
        self.appid = appid
    def __str__(self):
        return 'No metadata found for app ID {0} in "{1}"'.format(self.appid, EOS_CONTENT_JSON)

def load_as_app_from_appdata(appdata_file):
    app = AppStreamGlib.App()
    app.parse_file(appdata_file, AppStreamGlib.AppParseFlags.NONE)
    return app

class ShellContent:

    def __init__(self):
        self._translations, self._langs = self._get_translations_dict()
        # Regex for matching anything starting with a <tag> like format
        self._tag_expression = re.compile('^\s*\<\w+\>.*')

    def _get_translations_dict(self):
        """Get translations dictionary and list of languages.

        It reads the translations from a predefined file and returns a dictionary
        with the translated strings and a list of the available languages.
        """
        strings_dict = {}
        langs = []

        for lang in os.listdir(LOCALES_DIR):
            mo_file_path = os.path.join(LOCALES_DIR, lang, 'LC_MESSAGES', 'eos-shell-content.mo')
            if not os.path.exists(mo_file_path):
                continue
            langs.append(lang)
            mo_file = polib.mofile(mo_file_path)
            strings_dict[lang] = {(entry.msgid, entry.msgctxt): entry.msgstr for entry in mo_file}

        return (strings_dict, langs)

    def _get_app_metadata(self, app_id):
        all_metadata = json.load(open(EOS_CONTENT_JSON))

        for i in range(len(all_metadata)):
            metadata = all_metadata[i]
            metadata_id = metadata['application-id']
            if metadata_id == app_id:
                return metadata

            # Take into account "localized" IDs for Endless applications.
            # E.g. and app ID of "com.endlessm.howto" in the metadata is a valid
            # metadata for "com.endlessm.howto.en"
            components = app_id.rsplit('.', 1)
            unlocalized_id = components[0]
            try:
                locale = components[1]
            except:
                locale = ''

                # Check the locale component looks like a locale, and only apply
                # this heuristic for com.endlessm. applications
                if unlocalized_id.startswith('com.endlessm.') and \
                   (len(locale) == 2 or (len(locale) == 5 and locale[2] == '_')) and \
                   metadata_id == unlocalized_id:
                    return metadata

        return None

    def _translate_field(self, lang, field, msg):
        messages = self._translations.get(lang)
        if not messages:
            return ''
        return messages.get((msg, field), '')

    def _add_paragraph_tags_if_needed(self, text):
        if not text:
            return ''

        # Check if the parameter already looks like it's already formatted
        if self._tag_expression.match(text):
            return text

        # Otherwise format the text
        return '<p>{}</p>'.format(text)

    def _translate_app(self, app):
        for locale in self._langs:
            name = self._translate_field(locale, 'title', app.get_name('C'))
            if not name:
                continue

            summary = self._translate_field(locale, 'subtitle', app.get_comment('C'))
            description = self._translate_field(locale, 'description', app.get_description('C'))

            app.set_name(locale, name)
            if summary:
                app.set_comment(locale, summary)
            if description:
                app.set_description(locale, self._add_paragraph_tags_if_needed(description))

    def _get_screenshot_url(self, app_id, locale, image):
        return '{bucket}/screenshots/{app_id}/{locale}/{image}'.format(bucket=CMS_GS_BUCKET_URL,
                                                                       app_id=app_id,
                                                                       locale=locale,
                                                                       image=image)

    def update_app(self, app, content_app_id=''):
        app_id = content_app_id or app.get_id()
        metadata = self._get_app_metadata(app_id)

        if not metadata:
            app_id = app_id.rsplit('.desktop', 1)[0]
            metadata = self._get_app_metadata(app_id)

            if not metadata:
                raise NoMetadataException(app_id)

        app.set_name('C', metadata['title'])
        app.set_comment('C', metadata['subtitle'])
        description = metadata['description']
        app.set_description('C', description)

        categories = metadata.get('category')
        for category in categories.split(';'):
            app.add_category(category)

        # Screenshots in the metadata are arranged as 'language' -> ['image', ...]
        # but we need to group the same images in the same screenshot (with a
        # different language each), so we invert the arrangement as:
        # 'image' -> ['language', ...]
        #
        # Use an OrderedDict so we maintain the order of the screenshots as found
        # in the metadata which can be important.
        screenshots = collections.OrderedDict()
        for locale, images in metadata.get('screenshots', {}).items():
            for image in images:
                screenshots.setdefault(image, []).append(locale)

        for image, locales in screenshots.items():
            screenshot = AppStreamGlib.Screenshot()
            for locale in locales:
                as_img = AppStreamGlib.Image()
                # We need to add the screenshots as source, otherwise, without a
                # caption and other elements, AppStreamGlib discards the screenshots
                # as duplicates...
                as_img.set_kind(AppStreamGlib.ImageKind.SOURCE)
                as_img.set_url(self._get_screenshot_url(app_id, locale, image))
                if locale != 'C':
                    as_img.set_locale(locale)
                screenshot.add_image(as_img)
            app.add_screenshot(screenshot)

        self._translate_app(app)
        # We only format the description now otherwise it would not
        # match the translations
        app.set_description('C', self._add_paragraph_tags_if_needed(description))

    def _remove_unneeded_screenshots(self, xml_root):
        images = xml_root.findall('./screenshots/screenshot/image')
        has_shell_content_screenshots = False
        for image in images:
            if image.text.startswith(CMS_GS_BUCKET_URL):
                has_shell_content_screenshots = True
                break

        # Do not remove screenshots unless we have some of ours specified
        if not has_shell_content_screenshots:
            return

        # Remove all screenshots that had only images not starting with our URL
        screenshots = xml_root.find('screenshots')
        for screenshot in screenshots.getchildren():
            for image in screenshot.findall('image'):
                if not image.text.startswith(CMS_GS_BUCKET_URL):
                    screenshot.remove(image)
            if not screenshot.findall('image'):
                screenshots.remove(screenshot)

    def update_appdata_from_file(self, file_path, content_app_id=''):
        app = load_as_app_from_appdata(file_path)
        self.update_app(app, content_app_id)

        # Add a special metadata item in order to easily check if this app-data
        # file has been merged by eos-shell-content
        app.add_metadata('Endless::EosShellContent::Merged', 'true')

        store = AppStreamGlib.Store()
        store.add_app(app)
        xml_str = store.to_xml(AppStreamGlib.NodeToXmlFlags.NONE).str
        root = ET.fromstring(xml_str)
        if root.tag == 'components':
            root = root.find('component')

        # We do not want to display screenshots from 3rd parties when we have
        # provided some from the Shell Content, so we need to remove them.
        # The removal should be done in the app object but this cannot be
        # accomplished until there is API to do it in libappstream-glib.
        self._remove_unneeded_screenshots(root)

        node = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf-8'))
        return node.toprettyxml(indent='  ')
