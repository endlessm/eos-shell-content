#!/usr/bin/python

# This script generates desktop.in files for apps and links, which
# will later be translated via translate_desktop_files into .desktop files.
# These scripts require polib

# To use this script, first log into eoscms.parafernalia.net.br
# Under "App Store", click on "Generate Package"
# There should be no warnings
# Click on "Click here to download files in zip format"
# Save the downloaded file in this folder as appstore.zip
# Run this script
# Add and commit any changes to git
# Proceed with the normal build process

import os
import shutil
import sys
import zipfile
import collections
import json

from translate_desktop_files import translate_dir

IGNORE_ERRORS = True
LINKS_LOCALES = ['en-us', 'pt-br', 'es-gt']
ZIP_FILENAME = 'appstore.zip'
UNZIP_DIR = 'unzipped'
DATA_DIR = 'data'
LINKS_DIR = os.path.join(DATA_DIR, 'links')
APPS_DIR = os.path.join(DATA_DIR, 'applications')

class DesktopObject(object):

    DESKTOP_KEYS = [
        'Version',
        'Name',
        'Comment',
        'Type',
        'Exec',
        'Icon',
        'Categories',
        'X-Endless-ShowInAppStore',
    ]
        
    def __init__(self, data):
        self._locale_keys = ['Name', 'Comment', 'Icon']
        self._suffix = '.desktop.in'
        self._data = data

        self.defaults = {}
        self.defaults['Version'] = '1.0'
        self.defaults['Type'] = 'Application'

    def get(self, key):
        if key in self.json_keys:
            val = self._data[self.json_keys[key]]
            if key is 'Icon':
                return self._icon_prefix + val
            if key is 'Categories':
                if val is None:
                    return ''
                return ';'.join(val.split(' and ')) + ';'
            else:
                return val
        elif key in self.defaults:
            return self.defaults[key]
        elif key == 'X-Endless-ShowInAppStore':
            # If the app has no categories, it shouldn't be listed in the app store
            # Note: the strings must be all lower case,
            # so we cannot simply return a boolean value
            if self.get('Categories') == '':
                return 'false'
            else:
                return 'true'
        elif key == 'Position':
            folder = self.get('Folder')
            index = self.get('Index')
            if folder == 'none' or folder == '' or index is None:
                return None
            elif folder == 'desktop' or folder == 'default':
                return index
            else:
                return folder + ':' + index
        else:
            raise AttributeError

    def _write_key(self, handle, key):
        line = ('%s=%s\n' % (key, self.get(key))).encode('utf-8')
        if self.key_is_localized(key):
            line = '_' + line

        handle.write(line)
    
    def key_is_localized(self, key):
        return key in self._locale_keys

class LinkObject(DesktopObject):

    json_keys = {
        'Name': 'linkName',
        'Comment': 'linkSubtitle',
        'Categories': 'linkCategory',
        'Id': 'linkId',
        'Icon': 'linkId',
        'URL': 'linkUrl',
        'Index': 'linkDesktopPosition',
        'Folder': 'linkFolder',
    }

    def __init__(self, data, locale):
        super(LinkObject, self).__init__(data)
        self._desktop_dir = LINKS_DIR
        self._localized_urls = {
            locale: self.get('URL')
        }
        self._prefix = 'eos-link-'
        self._icon_prefix = 'eos-link-'

    def append_localized_url(self, locale, url):
        if url not in self._localized_urls:
            self._localized_urls[locale] = url

    def _get_exec(self):
        # If there's only one URL for this link, just return an exec which opens that url
        # in chromium. Otherwise, send each url with its respective locale to eos-exec-localized
        [default_locale, default_url] = self._localized_urls.items()[0]

        same_url = True
        for locale, url in self._localized_urls.items():
            if url != default_url:
                same_url = False
                break

        if same_url:
            return 'chromium-browser ' + default_url

        exec_str = 'eos-exec-localized '
        exec_str += '\'chromium-browser ' + default_url + '\' '

        for locale, url in self._localized_urls.items():
            exec_str += locale + ':\'chromium-browser ' + url + '\' '

        return exec_str

    def get(self, key):
        if key is 'Exec' or key is 'TryExec':
            return self._get_exec()
        else:
            return super(LinkObject, self).get(key)

class AppObject(DesktopObject):

    json_keys = {
        'Name': 'title',
        'Id': 'desktop-id',
        'Comment': 'subtitle',
        'Categories': 'category',
        'Exec': 'exec',
        'TryExec': 'tryexec',
        'Icon': 'application-id',
        'Folder': 'folder',
        'Index': 'desktop-position',
    }

    def __init__(self, data):
        super(AppObject, self).__init__(data)
        self._desktop_dir = APPS_DIR
        # For applications, the desktop-id already has the 'eos-app-' prefix
        self._prefix = ''
        self._icon_prefix = 'eos-app-'

if __name__ == '__main__':

    # Remove the existing unzipped and content dirs, if they exist
    shutil.rmtree(UNZIP_DIR, IGNORE_ERRORS)
    shutil.rmtree(LINKS_DIR, IGNORE_ERRORS)
    shutil.rmtree(APPS_DIR, IGNORE_ERRORS)

    # Unzip the file
    zfile = zipfile.ZipFile(ZIP_FILENAME)
    zfile.extractall(UNZIP_DIR)

    # Make the content dirs
    os.mkdir(LINKS_DIR)
    os.mkdir(APPS_DIR)

    # Each app/link will be indexed by its id, so that duplicates (resulting from
    # different locales) will be merged for i18n
    desktop_objects = {}

    # For now, links are stored on a per-locale basis in JSON files. The output desktop
    # file should combine all specified URLs, switching on the locale via eos-exec-localized
    for locale in LINKS_LOCALES:
        lang = locale.split('-')[0]
        localized_link_file = os.path.join(UNZIP_DIR, 'links', locale + '.json')
        localized_link_json = json.load(open(localized_link_file))
        for category in localized_link_json:
            for link_data in category['links']:
                id = link_data['linkId']
                if id not in desktop_objects.keys():
                    desktop_objects[id] = LinkObject(link_data, lang)
                else:
                    url = link_data['linkUrl']
                    desktop_objects[id].append_localized_url(lang, url)

    apps_file = os.path.join(UNZIP_DIR, 'apps', 'content.json')
    apps_json = json.load(open(apps_file))
    for app_data in apps_json:
        id = app_data['application-id']
        desktop_objects[id] = AppObject(app_data)

    # For each of the parsed links/apps, output a desktop.in file which will then be translated
    # via autotools
    for id, obj in desktop_objects.items():
        desktop_id = obj.get('Id')
        desktop_path = os.path.join(obj._desktop_dir, obj._prefix + desktop_id + obj._suffix)
        desktop_file = open(desktop_path, 'w')
        desktop_file.write('[Desktop Entry]\n')

        for key in obj.DESKTOP_KEYS:
           obj._write_key(desktop_file, key) 

    # translate the desktop.in files we generated
    translate_dir(LINKS_DIR)
    translate_dir(APPS_DIR)
