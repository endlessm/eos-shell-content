ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

SUBDIRS = content po data

EXTRA_DIST = \
	autogen.sh \
	COPYING \
	NEWS

# Distribute and install the entire acknowledgements directory
EXTRA_DIST += acknowledgements

install-data-local:
	mkdir -p $(DESTDIR)$(pkgdatadir)
	cp -r $(srcdir)/acknowledgements $(DESTDIR)$(datadir)/eos-acknowledgements
	chmod -R +w $(DESTDIR)$(datadir)/eos-acknowledgements

uninstall-local:
	rm -rf $(DESTDIR)$(datadir)/eos-acknowledgements
