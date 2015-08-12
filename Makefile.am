ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

SUBDIRS = tools content po data icons

EXTRA_DIST = \
	autogen.sh \
	COPYING \
	NEWS

# Distribute and install the entire bundle and image-attributions directories
EXTRA_DIST += bundle image-attributions
ACK_DIR = $(DESTDIR)$(datadir)/EndlessOS/acknowledgements

install-data-local:
	mkdir -p $(DESTDIR)$(pkgdatadir)
	cp -r $(srcdir)/bundle $(DESTDIR)$(pkgdatadir)
	chmod -R +w $(DESTDIR)$(pkgdatadir)/bundle
	mkdir -p $(ACK_DIR)
	cp -r $(srcdir)/image-attributions $(ACK_DIR)
	chmod -R +w $(ACK_DIR)/image-attributions

uninstall-local:
	rm -rf $(DESTDIR)$(pkgdatadir)/bundle
	rm -rf $(ACK_DIR)/image-attributions
