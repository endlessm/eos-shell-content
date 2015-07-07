# eoscontent.mk - dh_eoscontent integration for CDBS.
include /usr/share/cdbs/1/rules/debhelper.mk

CDBS_BUILD_DEPENDS_rules_eoscontent := eos-shell-content-dev
CDBS_BUILD_DEPENDS += , $(CDBS_BUILD_DEPENDS_rules_eoscontent)

$(patsubst %,binary-fixup/%,$(DEB_ALL_PACKAGES))::
	dh_eoscontent -p$(cdbs_curpkg) $(DEB_DH_EOSCONTENT_ARGS)
