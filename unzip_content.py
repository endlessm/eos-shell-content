#!/usr/bin/python

# This script requires installing ImageMagick
# (sudo apt-get install imagemagick)
# for the 'convert' command

# This script also requires polib
# (sudo apt-get install pip)
# (sudo pip install polib)

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
import json

from desktop_object import LinkObject, AppObject
from translate_desktop_files import translate_dir

ZIP_FILENAME = 'appstore.zip'
UNZIP_DIR = 'unzipped'
CONTENT_DIR = 'content/Default'
DATA_DIR = 'data'
LINKS_DIR = os.path.join(DATA_DIR, 'links')
APPS_DIR = os.path.join(DATA_DIR, 'applications')
SPLASH_DIR = '/usr/share/EndlessOS/splash'
IGNORE_ERRORS = True
JPEG_QUALITY = 90

# Run the ImageMagick 'convert' application from the command line,
# with specified JPEG quality and all metadata stripped
def convert(source, target, command):
    os.system('convert ' + source + ' ' + command +
              ' -quality ' + str(JPEG_QUALITY) + ' -strip ' + target)

if __name__ == '__main__':

    splash_dir = SPLASH_DIR

    if len(sys.argv) > 1:
        if len(sys.argv) == 3 and sys.argv[1] == '--splashdir':
            splash_dir = sys.argv[2]
        else:
            print('Usage: generate_desktop_files.py [--splashdir SPLASHDIR]')
            print('where SPLASHDIR is the folder where the splash images are installed')
            print('e.g. generate_desktop_files.py --splashdir /usr/share/EndlessOS/splash')

    # Remove the existing unzipped and content dirs, if they exist
    shutil.rmtree(UNZIP_DIR, IGNORE_ERRORS)
    shutil.rmtree(CONTENT_DIR, IGNORE_ERRORS)

    # Note: the unzipped directory does not currently match
    # the requirements of the app store, so we first unzip
    # into a staging area, and then copy individual files/folders
    # to the app store content directory

    # Unzip the file
    zfile = zipfile.ZipFile(ZIP_FILENAME)
    zfile.extractall(UNZIP_DIR)

    # For now, we need to convert specific locales to personalities,
    # including duplication of en-us as both default and Global,
    # and duplication of pt-br as both Brazil and Positivo,
    # until the CMS is reworked
    locales = ['en-us', 'en-us', 'es-gt', 'pt-br', 'pt-br']
    personalities = ['default', 'Global', 'Guatemala', 'Brazil', 'Positivo']

    # For now, we also need to convert specific locales to general languages
    # (with 'C' as the fallback for English) and personalities,
    # until the CMS is reworked
    languages = [None, 'C', 'es', 'pt', None]

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
        if (line.find('-screenshot') > 0):
            line = line.replace('.png', '.jpg')
        outfile.write(line)
    infile.close()
    outfile.close()

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

    # Copy and rename the links json to the content folder
    source_dir = os.path.join(UNZIP_DIR, 'links')
    target_dir = os.path.join(CONTENT_DIR, 'links')
    os.makedirs(target_dir)
    for i in range(0, len(locales)):
        # For now, we need to replace the CMS locale with personality
        # in the file names
        # Note: eventually, we will replace this with a single JSON
        # file that has all the links with a personality field for each link,
        # but for now let's minimize the changes to the CMS content files
        source = os.path.join(source_dir, locales[i] + '.json')
        target = os.path.join(target_dir, personalities[i] + '.json')
        shutil.copy(source, target)

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

    # Note: we are not yet handling the app and link icons

    # Note: we currently ignore the folder icons in the icons folder
    # They are .png files, where we currently need .svg files

    # Generate .desktop files

    # Remove the existing desktop dirs, if they exist
    shutil.rmtree(LINKS_DIR, IGNORE_ERRORS)
    shutil.rmtree(APPS_DIR, IGNORE_ERRORS)

    # Make the desktop dirs
    os.makedirs(LINKS_DIR)
    os.makedirs(APPS_DIR)

    # Each app/link will be indexed by its id, so that duplicates
    # (resulting from different locales) will be merged for i18n
    desktop_objects = {}

    # For now, links are stored on a per-locale basis in JSON files.
    # The output desktop file should combine all specified URLs,
    # switching on the locale via eos-exec-localized
    for i in range(0, len(locales)):
        if languages[i]:
            locale = locales[i]
            lang = locale.split('-')[0]
            localized_link_path = os.path.join(UNZIP_DIR, 'links', locale + '.json')
            localized_link_file = open(localized_link_path)
            localized_link_json = json.load(localized_link_file)
            localized_link_file.close()
            for category in localized_link_json:
                for link_data in category['links']:
                    id = link_data['linkId']
                    if id not in desktop_objects.keys():
                        desktop_objects[id] = LinkObject(link_data, LINKS_DIR,
                                                         splash_dir, lang)
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
        desktop_objects[id] = AppObject(app_data, APPS_DIR, splash_dir)

    # For each of the parsed links/apps, output a desktop.in file
    # which will then be translated via autotools
    for id, obj in desktop_objects.items():
        desktop_id = obj.get('Id')
        desktop_path = os.path.join(obj._desktop_dir, obj._prefix + desktop_id + obj._suffix)
        desktop_file = open(desktop_path, 'w')
        desktop_file.write('[Desktop Entry]\n')

        for key in obj.DESKTOP_KEYS:
           obj._write_key(desktop_file, key)

        desktop_file.close()

    # Translate the desktop.in files we generated
    translate_dir(LINKS_DIR)
    translate_dir(APPS_DIR)
