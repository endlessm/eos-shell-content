NULL =
EXTRA_DIST =
CLEANFILES =
DISTCLEANFILES =

default_app_json = \
	Default/apps/content.json \
	$(NULL)

EXTRA_DIST += $(default_app_json)

default_links_json = $(shell for file in `find Default/links -name "*.json"`; do printf "$$file "; done)

EXTRA_DIST += $(default_links_json)

default_app_images = $(shell for file in `find Default/apps/resources/images -name "*.jpg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_app_images)

default_app_thumbnails = $(shell for file in `find Default/apps/resources/thumbnails -name "*.jpg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_app_thumbnails)

default_app_screenshots = $(shell for file in `find Default/apps/resources/screenshots -name "*.jpg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_app_screenshots)

default_app_splash = $(shell for file in `find Default/apps/resources/splash -name "*.jpg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_app_splash)

default_links_images = $(shell for file in `find Default/links/images -name "*.jpg"`; do printf "$$file "; done)

EXTRA_DIST += $(default_links_images)

# extract-content-strings is a small utility that runs on the build system
extract_content_strings_sources = $(top_srcdir)/tools/extract-content-strings.c
extract_content_strings_cflags = $(EOS_SHELL_CONTENT_CFLAGS) $(MAINTAINER_CFLAGS)
extract_content_strings_ldadd = $(EOS_SHELL_CONTENT_LIBS)

extract-content-strings$(BUILD_EXEEXT): $(extract_content_strings_sources)
	@rm -f extract-content-strings$(BUILD_EXEEXT)
	$(AM_V_CCLD)$(CC) $(AM_CFLAGS) $(extract_content_strings_cflags) $^ $(extract_content_strings_ldadd) -o $@

EXTRA_DIST += $(extract_content_strings_sources)
DISTCLEANFILES += extract-content-strings$(BUILD_EXEEXT)

# we need to generate the json.h header because gettext does not know how
# to extract strings from custom JSON.
content_files = $(default_app_json) $(default_links_json)
content_headers = $(content_files:.json=.json.h)
%.json.h: $(content_files) extract-content-strings$(BUILD_EXEEXT)
	$(AM_V_GEN) ./extract-content-strings$(BUILD_EXEEXT) $(addsuffix .json,$*) > $@

all-local: $(content_headers)

CLEANFILES += $(content_headers)

contentdir = $(datadir)/application-store
nobase_content_DATA = \
	$(default_app_json) \
	$(default_app_images) \
	$(default_app_thumbnails) \
	$(default_app_screenshots) \
	$(default_links_json) \
	$(default_links_images) \
	$(NULL)

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
		      echo "    <file compressed=\"true\" alias=\"links/$$file\">$$file</file>" >> $@ ; \
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
	eos-app-store-link-content.gresource \
	$(NULL)

splashdir = $(datadir)/EndlessOS/splash
splash_DATA = $(default_app_splash)

CLEANFILES += \
	eos-app-store-app-content.gresource \
	eos-app-store-app-content.gresource.xml \
	eos-app-store-link-content.gresource \
	eos-app-store-link-content.gresource.xml \
	$(NULL)
