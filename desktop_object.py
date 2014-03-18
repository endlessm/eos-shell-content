import os

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
        
    def __init__(self, data, desktop_dir, splash_dir):
        self._locale_keys = ['Name', 'Comment']
        self._suffix = '.desktop.in'
        self._data = data
        self._desktop_dir = desktop_dir
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
            if key == 'X-Endless-SplashScreen':
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

    def __init__(self, data, desktop_dir, splash_dir, locale):
        super(LinkObject, self).__init__(data, desktop_dir, splash_dir)
        self._locales = [locale]
        self._localized_urls = {
            locale: self.get('URL')
        }
        self._prefix = 'eos-link-'
        self._icon_prefix = 'eos-link-'

        self.defaults['Personalities'] = ['All'];

    def append_localized_url(self, locale, url):
        if url not in self._localized_urls:
            self._locales.append(locale)
            self._localized_urls[locale] = url

    def _get_exec(self):
        # If there's only one URL for this link,
        # just return an exec which opens that url in chromium.
        # Otherwise, send each url with its respective locale 
        # to eos-exec-localized.
        default_locale = self._locales[0]
        default_url = self._localized_urls[default_locale]

        same_url = True
        for locale, url in self._localized_urls.items():
            if url != default_url:
                same_url = False
                break

        if same_url:
            return 'chromium-browser ' + default_url

        exec_str = 'eos-exec-localized '
        exec_str += '\'chromium-browser ' + default_url + '\' '

        # Process locales in the same order they were appended
        for locale in self._locales:
            url = self._localized_urls[locale]
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

    def __init__(self, data, desktop_dir, splash_dir):
        super(AppObject, self).__init__(data, desktop_dir, splash_dir)
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
