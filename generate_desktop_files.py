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
SPLASHDIR = '/usr/share/EndlessOS/splash'

MIME_TYPES = {
    'eos-app-com.endlessm.photos': 'image/bmp;image/gif;image/jpeg;image/jpg;image/pjpeg;image/png;image/tiff;image/x-bmp;image/x-gray;image/x-icb;image/x-ico;image/x-png;image/x-portable-anymap;image/x-portable-bitmap;image/x-portable-graymap;image/x-portable-pixmap;image/x-xbitmap;image/x-xpixmap;image/x-pcx;image/svg+xml;image/svg+xml-compressed;image/vnd.wap.wbmp;',
    'eos-app-shotwell': 'x-content/image-dcf;image/jpeg;image/jpg;image/pjpeg;image/png;image/tiff;image/x-3fr;image/x-adobe-dng;image/x-arw;image/x-bay;image/x-bmp;image/x-canon-cr2;image/x-canon-crw;image/x-cap;image/x-cr2;image/x-crw;image/x-dcr;image/x-dcraw;image/x-dcs;image/x-dng;image/x-drf;image/x-eip;image/x-erf;image/x-fff;image/x-fuji-raf;image/x-iiq;image/x-k25;image/x-kdc;image/x-mef;image/x-minolta-mrw;image/x-mos;image/x-mrw;image/x-nef;image/x-nikon-nef;image/x-nrw;image/x-olympus-orf;image/x-orf;image/x-panasonic-raw;image/x-pef;image/x-pentax-pef;image/x-png;image/x-ptx;image/x-pxn;image/x-r3d;image/x-raf;image/x-raw;image/x-raw;image/x-rw2;image/x-rwl;image/x-rwz;image/x-sigma-x3f;image/x-sony-arw;image/x-sony-sr2;image/x-sony-srf;image/x-sr2;image/x-srf;image/x-x3f;'
}

class DesktopObject(object):

    DESKTOP_KEYS = [
        'Version',
        'Name',
        'Comment',
        'Type',
        'Exec',
        'TryExec',
        'Icon',
        'Categories',
        'MimeType',
        'X-Endless-ShowInAppStore',
        'X-Endless-ShowInPersonalities',
        'X-Endless-SplashScreen',
        'X-Endless-SplashBackground'
    ]
        
    def __init__(self, data):
        self._locale_keys = ['Name', 'Comment']
        self._suffix = '.desktop.in'
        self._data = data

        self.defaults = {}
        self.defaults['Version'] = '1.0'
        self.defaults['Type'] = 'Application'

    def get(self, key):
        if key in self.json_keys:
            val = self._data[self.json_keys[key]]
            if key == 'Icon':
                return self._icon_prefix + val
            if key == 'TryExec':
                if not val:
                    # Convert empty string to None to avoid writing field
                    return None
                return val
            if key == 'Categories':
                if val is None:
                    return ''
                return ';'.join(val.split(' and ')) + ';'
            if key == 'X-Endless-SplashScreen':
                if val in ['Default', 'Custom']:
                    return 'true'
                else:
                    return 'false'
            if key == 'X-Endless-SplashBackground':
                if val:
                    if SPLASHDIR:
                        return os.path.join(SPLASHDIR, val)
                    else:
                        return val
                else:
                    return None
            else:
                return val
        elif key in self.defaults:
            return self.defaults[key]
        elif key == 'MimeType':
            id = self.get('Id')
            if id in MIME_TYPES:
                return MIME_TYPES[id]
            else:
                return None
        elif key == 'X-Endless-ShowInAppStore':
            # If the app has no categories, it shouldn't be listed in the app store
            # Note: the strings must be all lower case,
            # so we cannot simply return a boolean value
            if self.get('Categories') == '':
                return 'false'
            else:
                return 'true'
        elif key == 'X-Endless-ShowInPersonalities':
            personalities = self.get('Personalities')
            if 'All' in personalities:
                return None
            elif 'None' in personalities:
                return ''
            else:
                return ';'.join(personalities) + ';'
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
        val = self.get(key)
        if val is not None:
            line = ('%s=%s\n' % (key, val)).encode('utf-8')
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

        self.defaults['Personalities'] = ['All'];

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
        if key == 'Exec':
            return self._get_exec()
        elif key == 'TryExec':
            return None
        elif key == 'MimeType':
            return None
        elif key == 'X-Endless-SplashScreen':
            return None
        elif key == 'X-Endless-SplashBackground':
            return None
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
        'X-Endless-SplashScreen': 'splash-screen-type',
        'X-Endless-SplashBackground': 'custom-splash-screen'
    }

    def __init__(self, data):
        super(AppObject, self).__init__(data)
        self._desktop_dir = APPS_DIR
        # For applications, the desktop-id already has the 'eos-app-' prefix
        self._prefix = ''
        self._icon_prefix = 'eos-app-'

    def _get_personalities(self):
        personalities = self._data['personalities']
        return map(lambda p: 'default' if p == 'Default' else p, personalities)

    def get(self, key):
        if key == 'Personalities':
            return self._get_personalities()
        else:
            return super(AppObject, self).get(key)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        if len(sys.argv) == 3 and sys.argv[1] == '--splashdir' :
            SPLASHDIR = sys.argv[2]
        else :
            print('Usage: generate_desktop_files.py [--splashdir SPLASHDIR]')
            print('where SPLASHDIR is the folder where the splash images are installed')
            print('e.g. generate_desktop_files.py --splashdir /usr/share/EndlessOS/splash')

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
        localized_link_path = os.path.join(UNZIP_DIR, 'links', locale + '.json')
        localized_link_file = open(localized_link_path)
        localized_link_json = json.load(localized_link_file)
        localized_link_file.close()
        for category in localized_link_json:
            for link_data in category['links']:
                id = link_data['linkId']
                if id not in desktop_objects.keys():
                    desktop_objects[id] = LinkObject(link_data, lang)
                else:
                    url = link_data['linkUrl']
                    desktop_objects[id].append_localized_url(lang, url)

    apps_path = os.path.join(UNZIP_DIR, 'apps', 'content.json')
    apps_file = open(apps_path)
    apps_json = json.load(apps_file)
    apps_file.close()
    for app_data in apps_json:
        # Use desktop-id rather than application-id,
        # to ensure the ID is unique from any link IDs
        # Otherwise, for instance, we the wikipedia app would
        # clobber the wikipedia link in the dictionary
        id = app_data['desktop-id']
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

        desktop_file.close()

    # translate the desktop.in files we generated
    translate_dir(LINKS_DIR)
    translate_dir(APPS_DIR)
