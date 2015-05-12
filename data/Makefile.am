links_desktop_files = $(wildcard links/*.desktop)
applications_desktop_files = $(wildcard applications/*.desktop)

desktopsdir = $(datadir)/applications
desktops_DATA = \
    $(links_desktop_files) \
    $(applications_desktop_files) \
    $(NULL)

foldersdir = $(datadir)/desktop-directories
folders_DATA = $(wildcard folders/*.directory)

settingsdir = $(datadir)/EndlessOS/language-defaults
settings_DATA = $(wildcard settings/icon-grid-*.json)

do_subst = sed \
	-e 's|@DATA_DIR[@]|$(datadir)|g' \
	-e 's|@SYSCONF_DIR[@]|$(sysconfdir)|g'

eos-select-personality: eos-select-personality.in Makefile
	$(AM_V_GEN) $(do_subst) $< > $@
	chmod +x $@

eos-save-icon-grid: eos-save-icon-grid.in Makefile
	$(AM_V_GEN) $(do_subst) $< > $@
	chmod +x $@

EXTRA_DIST = \
    $(desktops_DATA) \
    $(folders_DATA) \
    $(settings_DATA) \
    eos-exec-localized \
    eos-select-personality.in \
    eos-save-icon-grid.in \
    $(NULL)

bin_SCRIPTS = \
    eos-exec-localized \
    eos-select-personality \
    eos-save-icon-grid \
    $(NULL)

CLEANFILES = \
    eos-select-personality \
    eos-save-icon-grid \
    $(NULL)
