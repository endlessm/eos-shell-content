ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

SUBDIRS = tools content po data icons

EXTRA_DIST = \
	autogen.sh \
	COPYING \
	NEWS

# Distribute and install the entire bundle and acknowledgements directories
EXTRA_DIST += bundle acknowledgements

install-data-local:
	mkdir -p $(DESTDIR)$(pkgdatadir)
	cp -r $(srcdir)/bundle $(DESTDIR)$(pkgdatadir)
	chmod -R +w $(DESTDIR)$(pkgdatadir)/bundle
	cp -r $(srcdir)/acknowledgements $(DESTDIR)$(datadir)/eos-acknowledgements

uninstall-local:
	rm -rf $(DESTDIR)$(pkgdatadir)/bundle
	rm -rf $(DESTDIR)$(datadir)/eos-acknowledgements
