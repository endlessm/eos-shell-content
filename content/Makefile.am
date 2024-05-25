NULL =
EXTRA_DIST =
MAINTAINERCLEANFILES =

default_folders_json = \
	folders.json \
	$(NULL)

EXTRA_DIST += $(default_folders_json)

# we need to generate the json.h header because gettext does not know
# how to extract strings from custom JSON. Generate them in the source
# directory since the po rules expect to find POTFILES there.
content_files = $(default_app_json) $(default_folders_json)
content_headers = $(content_files:.json=.json.h)
%.json.h: %.json
	$(top_builddir)/tools/extract-content-strings$(BUILD_EXEEXT) $< $(srcdir)/$@

# Distribute the json.h files so they don't need to be regenerated at
# build time
dist_noinst_DATA = $(content_headers)
MAINTAINERCLEANFILES += $(content_headers)
