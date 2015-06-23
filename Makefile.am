ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

SUBDIRS = content po data icons

EXTRA_DIST = \
	autogen.sh \
	COPYING \
	NEWS

# Distribute and install the entire bundle directory
EXTRA_DIST += bundle
install-data-local:
	mkdir -p $(DESTDIR)$(pkgdatadir)
	cp -r $(srcdir)/bundle $(DESTDIR)$(pkgdatadir)
	chmod -R +w $(DESTDIR)$(pkgdatadir)/bundle
uninstall-local:
	rm -rf $(DESTDIR)$(pkgdatadir)/bundle
