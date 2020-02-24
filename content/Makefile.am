NULL =
EXTRA_DIST =
CLEANFILES =
DISTCLEANFILES =
MAINTAINERCLEANFILES =

default_app_json = \
	Default/apps/content.json \
	$(NULL)

EXTRA_DIST += $(default_app_json)

app_jsondir = $(pkgdatadir)
app_json_DATA = $(default_app_json)

default_links_json := $(shell cd $(srcdir); for file in `find Default/links -name "*.json"`; do printf "$$file "; done)

EXTRA_DIST += $(default_links_json)

default_folders_json = \
	folders.json \
	$(NULL)

EXTRA_DIST += $(default_folders_json)

default_links_images := $(shell cd $(srcdir); for file in `find Default/links/images -name "*.jpg" -o -name "*.jpeg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_links_images)

# we need to generate the json.h header because gettext does not know
# how to extract strings from custom JSON. Generate them in the source
# directory since the po rules expect to find POTFILES there.
content_files = $(default_app_json) $(default_links_json) $(default_folders_json)
content_headers = $(content_files:.json=.json.h)
%.json.h: %.json
	$(top_builddir)/tools/extract-content-strings$(BUILD_EXEEXT) $< $(srcdir)/$@

# Distribute the json.h files so they don't need to be regenerated at
# build time
dist_noinst_DATA = $(content_headers)
MAINTAINERCLEANFILES += $(content_headers)

eos-app-store-link-content.gresource.xml: Makefile $(default_links_json) $(default_links_images)
	$(AM_V_GEN) ( echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" ; \
		      echo "<gresources>" ; \
		      echo "  <gresource prefix=\"/com/endlessm/appstore-content\">" ) > $@ ; \
		    for file in $(notdir $(default_links_json)); do \
		      echo "    <file alias=\"links/$$file\">$$file</file>" >> $@ ; \
		    done ; \
		    for file in $(notdir $(default_links_images)); do \
		      echo "    <file compressed=\"true\" alias=\"links/images/$$file\">$$file</file>" >> $@ ; \
		    done ; \
		    ( echo "  </gresource>" ; \
		      echo "</gresources>" ) >> $@

link_content_resource_files = $(shell $(GLIB_COMPILE_RESOURCES) \
	--sourcedir="$(srcdir)/Default/links" \
	--sourcedir="$(srcdir)/Default/links/images" \
	--generate-dependencies \
	eos-app-store-link-content.gresource.xml)

eos-app-store-link-content.gresource: eos-app-store-link-content.gresource.xml $(link_content_resource_files)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) \
		--target=$@ \
		--sourcedir="$(srcdir)/Default/links" \
		--sourcedir="$(srcdir)/Default/links/images" \
		$<

resourcedir = $(pkgdatadir)
resource_DATA = \
	eos-app-store-link-content.gresource \
	$(NULL)

CLEANFILES += \
	eos-app-store-link-content.gresource \
	eos-app-store-link-content.gresource.xml \
	$(NULL)
