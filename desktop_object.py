import os

MIME_TYPES = {
    'com.endlessm.photos': 'image/bmp;image/gif;image/jpeg;image/jpg;image/pjpeg;image/png;image/tiff;image/x-bmp;image/x-gray;image/x-icb;image/x-ico;image/x-png;image/x-portable-anymap;image/x-portable-bitmap;image/x-portable-graymap;image/x-portable-pixmap;image/x-xbitmap;image/x-xpixmap;image/x-pcx;image/svg+xml;image/svg+xml-compressed;image/vnd.wap.wbmp;',
    'shotwell': 'x-content/image-dcf;image/jpeg;image/jpg;image/pjpeg;image/png;image/tiff;image/x-3fr;image/x-adobe-dng;image/x-arw;image/x-bay;image/x-bmp;image/x-canon-cr2;image/x-canon-crw;image/x-cap;image/x-cr2;image/x-crw;image/x-dcr;image/x-dcraw;image/x-dcs;image/x-dng;image/x-drf;image/x-eip;image/x-erf;image/x-fff;image/x-fuji-raf;image/x-iiq;image/x-k25;image/x-kdc;image/x-mef;image/x-minolta-mrw;image/x-mos;image/x-mrw;image/x-nef;image/x-nikon-nef;image/x-nrw;image/x-olympus-orf;image/x-orf;image/x-panasonic-raw;image/x-pef;image/x-pentax-pef;image/x-png;image/x-ptx;image/x-pxn;image/x-r3d;image/x-raf;image/x-raw;image/x-raw;image/x-rw2;image/x-rwl;image/x-rwz;image/x-sigma-x3f;image/x-sony-arw;image/x-sony-sr2;image/x-sony-srf;image/x-sr2;image/x-srf;image/x-x3f;'
}

# Awful hack. Eventually, we want core apps to not use the installed
# eos-app-*.desktop files. Until we get there, we need to keep a list of
# apps that are converted so that the desktop files don't get installed
# in /usr/share/applications.
CORE_CONVERTED = ['gnome-terminal', 'chromium-browser', 'eos-file-manager',
                  'gnome-control-center', 'libreoffice-calc',
                  'libreoffice-impress', 'libreoffice-writer', 'rhythmbox',
                  'yelp', 'brasero', 'cheese', 'empathy', 'evolution',
                  'gedit']

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
        'X-Endless-LaunchMaximized',
        'X-Endless-SplashBackground'
    ]
        
    def __init__(self, data, splash_dir):
        self._locale_keys = ['Name', 'Comment']
        self._suffix = '.desktop.in'
        self._data = data
        self._splash_dir = splash_dir

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
            if key == 'X-Endless-LaunchMaximized':
                # In the CMS, the splash screen type serves a double duty:
                # if the type is 'None', we don't launch maximized
                if val in ['Default', 'Custom']:
                    return 'true'
                else:
                    return 'false'
            if key == 'X-Endless-SplashBackground':
                if val:
                    if self._splash_dir:
                        return os.path.join(self._splash_dir, val)
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

    def write_key(self, handle, key):
        val = self.get(key)
        if val is not None:
            line = '%s=%s\n' % (key, val)
            if self.key_is_localized(key):
                line = '_' + line

            handle.write(line)
    
    def key_is_localized(self, key):
        return key in self._locale_keys

    def get_desktop_path(self):
        return os.path.join(self.get_desktop_dir(),
                            self._prefix + self.get('Id') + self._suffix)

class LinkObject(DesktopObject):

    json_keys = {
        'Name': 'linkName',
        'Comment': 'linkSubtitle',
        'Categories': 'linkCategory',
        'Id': 'linkId',
        'Icon': 'linkId',
        'URL': 'linkUrl',
        'Index': 'linkDesktopPosition',
        'Folder': 'linkFolder'
    }

    def __init__(self, data, desktop_dir, splash_dir, locale):
        super(LinkObject, self).__init__(data, splash_dir)
        self._desktop_dir = desktop_dir
        self._default_name = self._data['linkName']
        self._name_locales = []
        self._localized_names = {}
        self._default_url = self.get('URL')
        self._url_locales = []
        self._localized_urls = {}
        self._prefix = 'eos-link-'
        self._icon_prefix = 'eos-link-'

    def append_localized_name(self, locale, name):
        if name != self._default_name:
            self._name_locales.append(locale)
            self._localized_names[locale] = name

    def append_localized_url(self, locale, url):
        if url != self._default_url:
            self._url_locales.append(locale)
            self._localized_urls[locale] = url

    def _get_names(self):
        name_string = self._default_name
        for locale in self._name_locales:
            name_string += '\nName[%s]=%s' % (locale,
                                              self._localized_names[locale])
        return name_string

    def _get_exec(self):
        # If there's only one URL for this link,
        # just return an exec which opens that url in chromium.
        if len(self._url_locales) == 0:
            return 'chromium-browser ' + self._default_url

        # Otherwise, send each url with its respective locale 
        # to eos-exec-localized.
        exec_str = 'eos-exec-localized '
        exec_str += '\'chromium-browser ' + self._default_url + '\' '

        # Process locales in the same order they were appended
        for locale in self._url_locales:
            url = self._localized_urls[locale]
            exec_str += locale + ':\'chromium-browser ' + url + '\' '

        return exec_str

    def get(self, key):
        if key == 'Name':
            return self._get_names()
        elif key == 'Exec':
            return self._get_exec()
        elif key in ['TryExec',
                     'MimeType',
                     'X-Endless-LaunchMaximized',
                     'X-Endless-SplashBackground']:
            return None
        else:
            return super(LinkObject, self).get(key)

    def get_desktop_dir(self):
        return self._desktop_dir

class AppObject(DesktopObject):

    json_keys = {
        'Name': 'title',
        'Id': 'application-id',
        'Core': 'core',
        'Personalities': 'personalities',
        'Comment': 'subtitle',
        'Categories': 'category',
        'Exec': 'exec',
        'TryExec': 'tryexec',
        'Icon': 'application-id',
        'Folder': 'folder',
        'Index': 'desktop-position',
        'X-Endless-LaunchMaximized': 'splash-screen-type',
        'X-Endless-SplashBackground': 'custom-splash-screen'
    }

    def __init__(self, data, desktop_dir, bundle_desktop_dir, splash_dir):
        super(AppObject, self).__init__(data, splash_dir)
        self._desktop_dir = desktop_dir
        self._bundle_desktop_dir = bundle_desktop_dir
        if self.get('Core') and self.get('Id') not in CORE_CONVERTED:
            self._prefix = 'eos-app-'
        else:
            self._prefix = ''
        self._icon_prefix = 'eos-app-'

    def get_desktop_dir(self):
        if self.get('Core') and self.get('Id') not in CORE_CONVERTED:
            return self._desktop_dir
        else:
            return self._bundle_desktop_dir

class FolderObject(DesktopObject):

    json_keys = {
        'Id': 'folderId',
        'Name': 'folderName',
        'Icon': 'folderIcon'
    }

    def __init__(self, data, desktop_dir):
        splash_dir = None
        super(FolderObject, self).__init__(data, splash_dir)
        self._desktop_dir = desktop_dir
        self._prefix = 'eos-folder-'
        self._icon_prefix = 'eos-folder-'
        self._suffix = '.directory.in'
        self.defaults['Type'] = 'Directory'

    def get(self, key):
        if key in ['Comment',
                   'Exec',
                   'TryExec',
                   'Categories',
                   'MimeType',
                   'X-Endless-LaunchMaximized',
                   'X-Endless-SplashBackground']:
            return None
        else:
            return super(FolderObject, self).get(key)

    def get_desktop_dir(self):
        return self._desktop_dir
