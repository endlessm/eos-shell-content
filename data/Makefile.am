foldersdir = $(datadir)/desktop-directories
folders_DATA = $(wildcard folders/*.directory)

settingsdir = $(pkgdatadir)/icon-grid-defaults
settings_DATA = $(wildcard settings/icon-grid-*.json)

TESTS = settings/validate-grid-json.py

do_subst = sed \
	-e 's|@PKG_DATA_DIR[@]|$(pkgdatadir)|g' \
	-e 's|@SYSCONF_DIR[@]|$(sysconfdir)|g'

eos-save-icon-grid: eos-save-icon-grid.in Makefile
	$(AM_V_GEN) $(do_subst) $< > $@
	chmod +x $@

EXTRA_DIST = \
    $(folders_DATA) \
    eos-save-icon-grid.in \
    $(NULL)

bin_SCRIPTS = \
    eos-save-icon-grid \
    $(NULL)

CLEANFILES = \
    eos-save-icon-grid \
    $(NULL)
