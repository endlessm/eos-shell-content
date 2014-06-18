icondir = $(datadir)/icons/EndlessOS

render_sizes = "64x64"
ICON_DIRS=$(shell SIZES="$(render_sizes)"; for size in $$SIZES; do for dir in `find $(srcdir)/$$size/* -type d`; do printf "$$dir,"; done; done;)
ICON_FILES=$(shell SIZES="$(render_sizes)"; for size in $$SIZES; do for file in `find $(srcdir)/$$size/* \( -name "*.png" -or -name "*.svg" \)`; do printf "$$file "; done; done;)

EXTRA_DIST = $(ICON_FILES)

install-data-local:
	for size in $(render_sizes); do \
		echo -e "Going to copy files for $$size"; \
		for file in `cd $(srcdir)/$$size && find . \( -name "*.png" -or -name "*.svg" \)`; do \
			context="`dirname $$file`"; \
			$(mkdir_p) $(DESTDIR)$(icondir)/$$size/$$context; \
			$(install_sh_DATA) $(srcdir)/$$size/$$file $(DESTDIR)$(icondir)/$$size/$$file; \
		done; \
	done

uninstall-local:
	for size in $(render_sizes); do \
		for file in `cd $(srcdir)/$$size && find . \( -name "*.png" -or -name "*.svg" \)`; do \
			rm -f $(DESTDIR)$(icondir)/$$size/$$file; \
		done; \
	done

install-data-hook:
	$(GTK_UPDATE_ICON_CACHE) -q -t $(DESTDIR)$(icondir)

uninstall-hook:
	@rm -f  $(DESTDIR)$(icondir)/icon-theme.cache
