NULL =
EXTRA_DIST =
CLEANFILES =
DISTCLEANFILES =

default_app_json = \
	Default/apps/content.json \
	$(NULL)

EXTRA_DIST += $(default_app_json)

default_links_json := $(shell cd $(srcdir); for file in `find Default/links -name "*.json"`; do printf "$$file "; done)

EXTRA_DIST += $(default_links_json)

default_folders_json = \
	folders.json \
	$(NULL)

EXTRA_DIST += $(default_folders_json)

default_app_images := $(shell cd $(srcdir); for file in `find Default/apps/resources/images -name "*.jpg" -o -name "*.jpeg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_app_images)

default_app_thumbnails := $(shell cd $(srcdir); for file in `find Default/apps/resources/thumbnails -name "*.jpg" -o -name "*.jpeg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_app_thumbnails)

default_app_screenshots := $(shell cd $(srcdir); for file in `find Default/apps/resources/screenshots -name "*.jpg" -o -name "*.jpeg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_app_screenshots)

default_app_splash := $(shell cd $(srcdir); for file in `find Default/apps/resources/splash -name "*.jpg" -o -name "*.jpeg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_app_splash)

default_links_images := $(shell cd $(srcdir); for file in `find Default/links/images -name "*.jpg" -o -name "*.jpeg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_links_images)

# we need to generate the json.h header because gettext does not know how
# to extract strings from custom JSON.
content_files = $(default_app_json) $(default_links_json) $(default_folders_json)
content_headers = $(content_files:.json=.json.h)
%.json.h: %.json $(top_builddir)/tools/extract-content-strings$(BUILD_EXEEXT)
	$(AM_V_GEN) $(MKDIR_P) $(@D) && \
	$(top_builddir)/tools/extract-content-strings$(BUILD_EXEEXT) $< $@

all-local: $(content_headers)

CLEANFILES += $(content_headers)

resource_screenshots := $(shell cd $(srcdir)/Default/apps/resources/screenshots; for file in `find * -name "*.jpg" -o -name "*.jpeg"`; do printf "$$file "; done)
eos-app-store-app-screenshots.gresource.xml: Makefile $(default_app_screenshots)
	$(AM_V_GEN) ( echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" ; \
		      echo "<gresources>" ; \
		      echo "  <gresource prefix=\"/com/endlessm/appstore-content\">" ) > $@ ; \
		    for file in $(resource_screenshots); do \
		      echo "    <file compressed=\"true\" alias=\"screenshots/$$file\">$$file</file>" >> $@ ; \
		    done ; \
		    ( echo "  </gresource>" ; \
		      echo "</gresources>" ) >> $@

app_screenshots_resource_files = $(shell $(GLIB_COMPILE_RESOURCES) \
	--sourcedir="$(srcdir)/Default/apps/resources/screenshots" \
	--generate-dependencies \
	eos-app-store-app-screenshots.gresource.xml)

eos-app-store-app-screenshots.gresource: eos-app-store-app-screenshots.gresource.xml $(app_screenshots_resource_files)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) \
		--target=$@ \
		--sourcedir="$(srcdir)/Default/apps/resources/screenshots" \
		$<

eos-app-store-app-content.gresource.xml: Makefile $(default_app_json) $(default_app_images) $(default_app_thumbnails)
	$(AM_V_GEN) ( echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" ; \
		      echo "<gresources>" ; \
		      echo "  <gresource prefix=\"/com/endlessm/appstore-content\">" ; \
		      echo "    <file alias=\"apps/$(notdir $(default_app_json))\">$(notdir $(default_app_json))</file>" ) > $@ ; \
		    for file in $(notdir $(default_app_images)); do \
		      echo "    <file compressed=\"true\" alias=\"apps/$$file\">$$file</file>" >> $@ ; \
		    done ; \
		    for file in $(notdir $(default_app_thumbnails)); do \
		      echo "    <file compressed=\"true\" alias=\"apps/$$file\">$$file</file>" >> $@ ; \
		    done ; \
		    ( echo "  </gresource>" ; \
		      echo "</gresources>" ) >> $@

app_content_resource_files = $(shell $(GLIB_COMPILE_RESOURCES) \
	--sourcedir="$(srcdir)/Default/apps" \
	--sourcedir="$(srcdir)/Default/apps/resources/images" \
	--sourcedir="$(srcdir)/Default/apps/resources/thumbnails" \
	--generate-dependencies \
	eos-app-store-app-content.gresource.xml)

eos-app-store-app-content.gresource: eos-app-store-app-content.gresource.xml $(app_content_resource_files)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) \
		--target=$@ \
		--sourcedir="$(srcdir)/Default/apps" \
		--sourcedir="$(srcdir)/Default/apps/resources/images" \
		--sourcedir="$(srcdir)/Default/apps/resources/thumbnails" \
		$<

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
	eos-app-store-app-content.gresource \
	eos-app-store-app-screenshots.gresource \
	eos-app-store-link-content.gresource \
	$(NULL)

splashdir = $(datadir)/EndlessOS/splash
splash_DATA = $(default_app_splash)

CLEANFILES += \
	eos-app-store-app-content.gresource \
	eos-app-store-app-content.gresource.xml \
	eos-app-store-app-screenshots.gresource \
	eos-app-store-app-screenshots.gresource.xml \
	eos-app-store-link-content.gresource \
	eos-app-store-link-content.gresource.xml \
	$(NULL)
