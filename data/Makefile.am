foldersdir = $(datadir)/desktop-directories
folders_DATA = $(wildcard folders/*.directory)

settingsdir = $(pkgdatadir)/icon-grid-defaults
settings_in_files = $(wildcard settings/icon-grid-*.json.in)
settings_DATA = $(settings_in_files:.in=)
dist_noinst_SCRIPTS = settings/write-grid-json.py

%.json: %.json.in settings/write-grid-json.py
	$(AM_V_GEN)$(srcdir)/settings/write-grid-json.py -o $@ \
		$<

do_subst = sed \
	-e 's|@PKG_DATA_DIR[@]|$(pkgdatadir)|g' \
	-e 's|@SYSCONF_DIR[@]|$(sysconfdir)|g'

eos-save-icon-grid: eos-save-icon-grid.in Makefile
	$(AM_V_GEN) $(do_subst) $< > $@
	chmod +x $@

EXTRA_DIST = \
    $(folders_DATA) \
    $(settings_in_files) \
    eos-save-icon-grid.in \
    $(NULL)

bin_SCRIPTS = \
    eos-save-icon-grid \
    $(NULL)

CLEANFILES = \
    $(settings_DATA) \
    eos-save-icon-grid \
    $(NULL)
