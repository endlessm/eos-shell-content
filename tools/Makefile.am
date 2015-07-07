NULL =
EXTRA_DIST =
CLEANFILES =
DISTCLEANFILES =

# extract-content-strings is a small utility that runs on the build system
noinst_PROGRAMS = \
	extract-content-strings \
	$(NULL)
extract_content_strings_CFLAGS = \
	$(EOS_SHELL_CONTENT_CFLAGS) \
	$(MAINTAINER_CFLAGS) \
	$(NULL)
extract_content_strings_LDADD = \
	$(EOS_SHELL_CONTENT_LIBS) \
	$(NULL)

dist_bin_SCRIPTS = \
	eos-content-merge \
	dh_eoscontent \
	$(NULL)

# Generate dh_eoscontent man page
man_MANS = dh_eoscontent.1
CLEANFILES += $(man_MANS)
POD2MAN_ARGS = --utf8 -c "$(PACKAGE_NAME)" -r "$(PACKAGE_VERSION)"
dh_eoscontent.1: dh_eoscontent
	$(AM_V_GEN)$(POD2MAN) $(POD2MAN_ARGS) $< $@

# Debhelper sequence file
debhelperdir = $(datadir)/perl5/Debian/Debhelper/Sequence
dist_debhelper_DATA = eoscontent.pm

# CDBS rules file
cdbsdir = $(datadir)/cdbs/1/rules
dist_cdbs_DATA = eoscontent.mk
