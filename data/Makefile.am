links_desktop_files = $(wildcard links/*.desktop)

desktopsdir = $(datadir)/applications
desktops_DATA = \
    $(links_desktop_files) \
    $(NULL)

foldersdir = $(datadir)/desktop-directories
folders_DATA = $(wildcard folders/*.directory)

settingsdir = $(datadir)/EndlessOS/language-defaults
settings_in_files = $(wildcard settings/icon-grid-*.json.in)
settings_DATA = $(settings_in_files:.in=)
dist_noinst_SCRIPTS = settings/write-grid-json.py

%.json: %.json.in settings/arch-blacklist.json
	$(AM_V_GEN)$(srcdir)/settings/write-grid-json.py -o $@ $^ $(host_cpu)

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
    $(settings_in_files) \
    settings/arch-blacklist.json \
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
    $(settings_DATA) \
    eos-select-personality \
    eos-save-icon-grid \
    $(NULL)
