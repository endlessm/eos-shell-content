#!/usr/bin/env python3

# This script requires installing ImageMagick
# (sudo apt-get install imagemagick)
# for the 'convert' command

# This script also requires polib
# (sudo apt-get install python3-polib)
# for the imported translate_desktop_files

# To use this script, first log into eoscms.parafernalia.net.br
# Under "App Store", click on "Generate Package"
# There should be no warnings
# Click on "Click here to download files in zip format"
# Save the downloaded file in this folder as appstore.zip
# Run this script
# Add and commit any changes to git
# Proceed with the normal build process

import copy
import json
import operator
import os
import shutil
import sys
import zipfile

from desktop_object import LinkObject, AppObject, FolderObject
from extra_categories import EXTRA_CATEGORIES
from extra_desktop_entries import EXTRA_DESKTOP_ENTRIES
from translate_desktop_files import translate_dir

ZIP_FILENAME = 'appstore.zip'
UNZIP_DIR = 'unzipped'
CONTENT_DIR = 'content/Default'
DATA_DIR = 'data'
BUNDLE_DIR = 'bundle'
LINKS_DIR = os.path.join(DATA_DIR, 'links')
BUNDLE_APPS_DIR = os.path.join(BUNDLE_DIR, 'desktops')
FOLDERS_DIR = os.path.join(DATA_DIR, 'folders')
BUNDLE_MANIFESTS_DIR = os.path.join(BUNDLE_DIR, 'manifests')
BUNDLE_ICON_DIR = os.path.join('icons', 'bundle', '64x64', 'apps')
CORE_ICON_DIR = os.path.join('icons', 'core', '64x64', 'apps')
ICON_MASK = '/tmp/icon_mask.png'
IGNORE_ERRORS = True
JPEG_QUALITY = 90
APP_PREFIX = 'eos-app-'
LINK_PREFIX = 'eos-link-'

# Run the ImageMagick 'convert' application from the command line,
# with specified JPEG quality and all metadata stripped
def convert(source, target, command):
    os.system('convert ' + source + ' ' + command +
              ' -quality ' + str(JPEG_QUALITY) + ' -strip ' + target)

# Use ImageMagick to round the corners based on a 60x60 square
# with radius 15 rounding centered within the 64x64 asset
def round_icon(source, target, command):
    os.system('convert ' + source + ' ' + command + ' -matte ' + ICON_MASK +
              ' -compose DstIn -composite' +
              ' -strip -define png:exclude-chunks=date,time ' + target)

# Return the path to the default designer icon, or None if it doesn't exist
def get_icon_path(linkJSON):
    # If the link object's icon path is just 'icons', there isn't a default designer icon
    if linkJSON['linkIcon'] == 'icons/':
        return None
    return linkJSON['linkIcon']

if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser(description='Generate desktop files')
    parser.add_argument('zipfile', nargs='?', default=ZIP_FILENAME,
                        help='zip file to unpack')
    args = parser.parse_args()

    # Create the icon mask for cropping with rounded corners
    # Note: 61,61 is the bottom-right coordinate, not the size
    # of the rounded rectangle (which is 60x60 in this case)
    os.system('convert -size 64x64 xc:none ' +
              '-draw "roundrectangle 2,2,61,61,15,15" ' + ICON_MASK)

    # Remove the existing unzipped and content dirs, if they exist
    shutil.rmtree(UNZIP_DIR, IGNORE_ERRORS)
    shutil.rmtree(CONTENT_DIR, IGNORE_ERRORS)

    # Note: the unzipped directory does not currently match
    # the requirements of the app store, so we first unzip
    # into a staging area, and then copy individual files/folders
    # to the app store content directory

    # Unzip the file
    zfile = zipfile.ZipFile(args.zipfile)
    zfile.extractall(UNZIP_DIR)

    # Although the CMS allows thumbnails to be provided as PNG,
    # we really want them to be JPG, both due to the smaller
    # compressed size and due to this script processing the PNG
    # files in such a way that every run of the script would
    # create useless metadata changes that lead to extra
    # git commits
    # Perhaps we could convert them here, but for now let's push
    # back and make sure they are in the CMS in the correct format
    png_thumbs = []
    thumbs_dir = os.path.join(UNZIP_DIR, 'apps', 'thumbs')
    for filename in os.listdir(thumbs_dir):
        if filename.endswith('.png'):
            png_thumbs.append(filename)
    if png_thumbs:
        print('Please replace the following PNG assets in the CMS with JPG:')
        for filename in png_thumbs:
            print(filename)
        exit()

    # Split the Spanish links by Global vs. Mexico
    # Unlike Guatemala, which is treated via a separate language
    # in the CMS, we don't have a separate language for Mexico
    json_dir = os.path.join(UNZIP_DIR, 'links')
    es_path = os.path.join(json_dir, 'es.json')
    mx_path = os.path.join(json_dir, 'es-mx.json')
    with open(es_path) as infile:
        json_data = json.load(infile)
    for path, region in [[es_path, 'Global'], [mx_path, 'Mexico']]:
        json_copy = copy.deepcopy(json_data)
        for category in json_copy:
            links = category['links']
            # Iterate over a copy of the list, since it is not safe
            # to remove an item from a list being iterated
            for link in list(links):
                link_region = link['linkRegion']
                if link_region != region:
                    links.remove(link)
        with open(path, 'w') as outfile:
            json.dump(json_copy, outfile, indent=2)

    # For now, we need to convert specific locales to personalities,
    # including duplication of en-us as both default and Global,
    # until the CMS is reworked
    locales = ['en-us', 'en-us', 'es-gt', 'pt-br', 'zh_CN', 'ar', 'bn']
    personalities = ['default', 'Global', 'Guatemala', 'Brazil', 'China', 'Arabic', 'Bengali']

    # For now, we also need to convert specific locales to general languages
    # (with 'C' as the fallback for English) and personalities,
    # until the CMS is reworked
    languages = [None, 'C', 'es', 'pt', 'zh_CN', 'ar', 'bn']

    # Copy the app json to the content folder
    # with tweaks to the json content
    source = os.path.join(UNZIP_DIR, 'apps', 'content.json')
    target_dir = os.path.join(CONTENT_DIR, 'apps')
    target = os.path.join(target_dir, 'content.json')
    os.makedirs(target_dir)
    infile = open(source, 'r')
    outfile = open(target, 'w')
    for line in infile:
        for i in range(0, len(locales)):
            if languages[i]:
                from_string = '"' + locales[i] + '"'
                to_string = '"' + languages[i] + '"'
                line = line.replace(from_string, to_string)
        if (line.find('-screenshot') >= 0):
            line = line.replace('.png', '.jpg')
        outfile.write(line)
    infile.close()
    outfile.close()

    # Re-write the JSON file sorted alphabetically by id,
    # and with keys sorted so that application-id is first
    # (for convenience in manually reviewing the file),
    # and with extra categories included (and with trailing
    # semicolon to match the freedesktop spec)
    with open(target) as infile:
        json_data = json.load(infile)
    for app_data in json_data:
        app_id = app_data['application-id']
        if not app_data.get('category', None):
            raise ValueError('No category for App ID %s' % app_id)
        categories = app_data['category'] + ';'
        extra_categories = EXTRA_CATEGORIES.get(app_id, [])
        for extra_category in extra_categories:
            categories += extra_category + ';'
        app_data['category'] = categories
    sorted_json = sorted(json_data, key=operator.itemgetter('application-id'))

    with open(target, 'w') as outfile:
        json.dump(sorted_json, outfile, indent=2, sort_keys=True)

    # Copy the thumbnail images to the content folder
    # with tweaked compression
    source_dir = os.path.join(UNZIP_DIR, 'apps', 'thumbs')
    target_dir = os.path.join(CONTENT_DIR, 'apps', 'resources', 'thumbnails')
    os.makedirs(target_dir)
    for source in os.listdir(source_dir):
        target = source
        source_file = os.path.join(source_dir, source)
        target_file = os.path.join(target_dir, target)
        convert(source_file, target_file, '')

    # Copy the featured images to the content folder
    # with tweaked compression
    # (Note: if the featured image is square, we just use the thumbnail)
    source_dir = os.path.join(UNZIP_DIR, 'apps', 'featured')
    target_dir = os.path.join(CONTENT_DIR, 'apps', 'resources', 'images')
    os.makedirs(target_dir)
    for source in os.listdir(source_dir):
        target = source
        source_file = os.path.join(source_dir, source)
        target_file = os.path.join(target_dir, target)
        convert(source_file, target_file, '')

    # Copy the screenshot images to the content folder
    # resized to a width of 480 pixels,
    # converting PNG to JPG as necessary
    # (Note: if the featured image is square, we just use the thumbnail)
    for i in range(0, len(locales)):
        if languages[i]:
            # For now, we need to replace the CMS locale with generic language
            # in the folder names
            source_dir = os.path.join(UNZIP_DIR, 'apps', 'screenshots', locales[i])
            target_dir = os.path.join(CONTENT_DIR, 'apps', 'resources',
                                      'screenshots', languages[i])
            os.makedirs(target_dir)
            for source in os.listdir(source_dir):
                target = source.replace('.png', '.jpg')
                fourth_screenshot_idx = target.find('4.jpg')
                if fourth_screenshot_idx > 0:
                    print('Warning: ' + languages[i] + ' ' +
                          target[0:fourth_screenshot_idx] +
                          ' has more than 3 screenshots')
                source_file = os.path.join(source_dir, source)
                target_file = os.path.join(target_dir, target)
                # Resize to a width of 480, allowing an arbitrary height
                convert(source_file, target_file,
                        '-resize 480x480')

    # Copy the splash screen images to the content folder
    # with tweaked compression
    source_dir = os.path.join(UNZIP_DIR, 'apps', 'splash')
    target_dir = os.path.join(CONTENT_DIR, 'apps', 'resources', 'splash')
    os.makedirs(target_dir)
    for source in os.listdir(source_dir):
        target = source
        source_file = os.path.join(source_dir, source)
        target_file = os.path.join(target_dir, target)
        convert(source_file, target_file, '')

    # Special handling of link locales for es vs. es_GT
    link_locales = [['en-us'], ['es'], ['es', 'es-gt'], ['es', 'es-mx'], ['pt-br'], ['zh-hans'], ['bn'], ['id'], ['th'], ['vi']]
    link_languages = ['C', 'es', 'es_GT', 'es_MX', 'pt_BR', 'zh_CN', 'bn', 'id', 'th', 'vi']

    # Copy and rename the links json to the content folder
    source_dir = os.path.join(UNZIP_DIR, 'links')
    target_dir = os.path.join(CONTENT_DIR, 'links')
    os.makedirs(target_dir)
    for i in range(0, len(link_locales)):
        # For now, we need to replace the CMS locale with language
        # in the file names
        json_data = []
        for locale in link_locales[i]:
            source = os.path.join(source_dir, locale + '.json')

            with open(source) as infile:
                locale_data = json.load(infile)
            for category in locale_data:
                category_name = category['category']
                found = False
                for json_category in json_data:
                    if json_category['category'] == category_name:
                        found = True
                        json_category['links'] += category['links']
                if not found:
                    json_data.append(category)

        # Write the JSON file sorted alphabetically by id
        # and with keys sorted
        # (for convenience in manually reviewing the file)
        for category in json_data:
            sorted_links = sorted(category['links'],
                                  key=operator.itemgetter('linkId'))
            category['links'] = sorted_links
        target = os.path.join(target_dir, link_languages[i] + '.json')
        with open(target, 'w') as outfile:
            json.dump(json_data, outfile, indent=2, sort_keys='True')

    # Copy the link images to the content folder
    # resized/cropped to 90x90
    source_dir = os.path.join(UNZIP_DIR, 'links', 'images')
    target_dir = os.path.join(CONTENT_DIR, 'links', 'images')
    os.makedirs(target_dir)
    for source in os.listdir(source_dir):
        target = source
        source_file = os.path.join(source_dir, source)
        target_file = os.path.join(target_dir, target)
        # In case the image is rectangular,
        # first resize so that the smallest dimension is 90 pixels,
        # then crop from the center to exactly 90x90
        convert(source_file, target_file,
                '-resize 90x90^ -gravity center -crop 90x90+0+0')

    # Note: we currently ignore the folder icons in the icons folder
    # They are .png files, where we currently need .svg files
    # Folder icons are currently managed in eos-theme

    # Generate .desktop files

    # Remove the existing desktop dirs, if they exist
    shutil.rmtree(LINKS_DIR, IGNORE_ERRORS)
    shutil.rmtree(BUNDLE_APPS_DIR, IGNORE_ERRORS)
    shutil.rmtree(FOLDERS_DIR, IGNORE_ERRORS)

    # Make the desktop dirs
    os.makedirs(LINKS_DIR)
    os.makedirs(BUNDLE_APPS_DIR)
    os.makedirs(FOLDERS_DIR)

    # Each app/link will be indexed by its id, so that duplicates
    # (resulting from different locales) will be merged for i18n
    desktop_objects = {}

    # For now, links are stored on a per-locale basis in JSON files.
    # The output desktop file should combine all specified URLs,
    # switching on the locale via eos-exec-localized
    for i in range(0, len(link_locales)):
        # Note: link locales are ordered so that the one of interest here
        # (i.e., the most localized) is the last one in the list
        locale = link_locales[i][-1]
        lang = locale.split('-')[0]
        localized_link_path = os.path.join(UNZIP_DIR, 'links', locale + '.json')
        localized_link_file = open(localized_link_path)
        localized_link_json = json.load(localized_link_file)
        localized_link_file.close()
        for category in localized_link_json:
            for link_data in category['links']:
                id = 'eos-link-' + link_data['linkId']
                if id not in desktop_objects.keys():
                    desktop_objects[id] = LinkObject(link_data, LINKS_DIR, lang)
                else:
                    name = link_data['linkName']
                    desktop_objects[id].append_localized_name(lang, name)
                    url = link_data['linkUrl']
                    desktop_objects[id].append_localized_url(lang, url)

    apps_path = os.path.join(CONTENT_DIR, 'apps', 'content.json')
    apps_file = open(apps_path)
    apps_json = json.load(apps_file)
    apps_file.close()
    for app_data in apps_json:
        id = app_data['application-id']
        desktop_objects[id] = AppObject(app_data, BUNDLE_APPS_DIR)

    # For now, the folders.json is not in the CMS output,
    # so we hard-code it in the directory above the processed content
    folders_path = os.path.join(CONTENT_DIR, '..', 'folders.json')
    folders_file = open(folders_path)
    folders_json = json.load(folders_file)
    folders_file.close()
    for folders_data in folders_json:
        id = folders_data['folderId']
        desktop_objects[id] = FolderObject(folders_data, FOLDERS_DIR)

    # For each of the parsed links/apps/folders, output a .in file
    # (desktop.in for links/apps, directory.in for folders)
    for id, obj in desktop_objects.items():
        desktop_path = obj.get_desktop_path()
        desktop_file = open(desktop_path, 'w')
        desktop_file.write('[Desktop Entry]\n')

        for key in obj.DESKTOP_KEYS:
           obj.write_key(desktop_file, key)

        # XXX: We need to add a few more entries based on which app we're
        # processing that we don't have support in the CMS for
        extra_entries = EXTRA_DESKTOP_ENTRIES.get(id, {})
        for key, value in extra_entries.items():
            desktop_file.write("{}={}".format(key, value))

        desktop_file.close()

    # Translate the .in files we generated
    translate_dir(LINKS_DIR)
    translate_dir(BUNDLE_APPS_DIR)
    translate_dir(FOLDERS_DIR)

    # Remove the existing icon dirs, if they exists
    shutil.rmtree(BUNDLE_ICON_DIR, IGNORE_ERRORS)
    shutil.rmtree(CORE_ICON_DIR, IGNORE_ERRORS)

    # Make the icon dirs
    os.makedirs(BUNDLE_ICON_DIR)
    os.makedirs(CORE_ICON_DIR)

    # Process and rename the app icons to the icon folder
    source_dir = os.path.join(UNZIP_DIR, 'apps', 'icons')
    for app_data in apps_json:
        # Rename the icons from name-icon.png to eos-app-name.png
        # Note that the CMS does not respect capitalization
        # in the source icon name, so we need to generate the
        # target file name based on the actual app ID
        source = app_data['icon']
        target = APP_PREFIX + app_data['application-id'] + '.png'
        if app_data['core']:
            target_dir = CORE_ICON_DIR
        else:
            target_dir = BUNDLE_ICON_DIR
        source_file = os.path.join(source_dir, source)
        target_file = os.path.join(target_dir, target)
        round_icon(source_file, target_file, '')

    # Process and rename the link icons to the icon folder
    # If no link icon available, resize/crop the thumbnail image
    source_dir = os.path.join(UNZIP_DIR, 'links')
    target_dir = CORE_ICON_DIR

    file_names = os.listdir(source_dir)

    # Work around the fact that the CMS currently splits
    # the links into separate JSON files by country
    for file_name in file_names:
        if file_name.endswith('.json'):
            links_json = os.path.join(source_dir, file_name)

            with open(links_json) as links_content:
                link_data = json.load(links_content)
                for category in link_data:
                    for link in category['links']:
                        icon_path = get_icon_path(link)
                        target_file = os.path.join(target_dir, LINK_PREFIX + link['linkId'] + '.png')

                        if icon_path is None:
                            # Generate a new icon based on existing link image
                            source_file = os.path.join(source_dir, 'images', link['linkId'] + '.jpg')
                            round_icon(source_file, target_file,
                                       '-resize 64x64^ -gravity center -crop 64x64+0+0')
                        else:
                            # Simply round existing icon asset to destination
                            source_file = os.path.join(source_dir, icon_path)
                            round_icon(source_file, target_file, '')

    # Generate bundle manifests for the image builder by personality

    shutil.rmtree(BUNDLE_MANIFESTS_DIR, IGNORE_ERRORS)
    os.makedirs(BUNDLE_MANIFESTS_DIR)

    # Map from personality to two-character language code(s)
    langs = {}
    for i in range(0, len(personalities)):
        lang = locales[i].split('-')[0]
        langs[personalities[i]] = lang
    all_langs = list(set(langs.values()))

    # For each personality, write a manifest of all the app bundles
    # (useful in maintaining the image builder manifests in eos-obs-build)
    for personality in personalities + ['all']:
        app_ids = []
        for id, obj in desktop_objects.items():
            if isinstance(obj, AppObject) \
                    and not obj.get('Core'):
                if personality == 'default':
                    continue
                elif personality == 'all':
                    app_ids.append(id)
                else:
                    app_personalities = obj.get('Personalities')
                    if 'All' in app_personalities \
                            or personality in app_personalities:
                        app_ids.append(id)
        app_ids.sort()
        manifest_path = os.path.join(BUNDLE_MANIFESTS_DIR,
                                     'bundle-manifest-%s.txt' % personality)
        with open(manifest_path, 'w') as manifest_file:
            for app in app_ids:
                manifest_file.write(app + '\n')

    # Generate a manifest of all the core apps
    # (useful in maintaining the core list in eos-meta)
    core_apps = []
    for id, obj in desktop_objects.items():
        if isinstance(obj, AppObject) and obj.get('Core'):
            core_apps.append(id)
    core_apps.sort()
    manifest_path = os.path.join(BUNDLE_MANIFESTS_DIR, 'core-manifest.txt')
    with open(manifest_path, 'w') as manifest_file:
        for app in core_apps:
            manifest_file.write(app + '\n')

    # Generate a manifest of all the apps by category
    category_apps = {}
    for id, obj in desktop_objects.items():
        if isinstance(obj, AppObject):
            categories = obj.get('Categories')
            # Drop the terminal ';' from the category list
            categories = categories[:len(categories)-1]
            for category in categories.split(';'):
                if category not in category_apps:
                    category_apps[category] = []
                category_apps[category].append(id)
    categories_path = os.path.join(BUNDLE_MANIFESTS_DIR, 'categories.txt')
    with open(categories_path, 'w') as categories_file:
        for category in sorted(category_apps.keys()):
            categories_file.write(category + ':\n')
            app_list = category_apps[category]
            app_list.sort()
            for app in app_list:
                categories_file.write(app + '\n')
            categories_file.write('\n')
