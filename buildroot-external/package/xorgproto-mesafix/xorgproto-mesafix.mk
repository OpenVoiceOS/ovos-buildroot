################################################################################
#
# xorgproto
#
################################################################################

XORGPROTO_MESAFIX_VERSION = 2021.5
XORGPROTO_MESAFIX_SOURCE = xorgproto-$(XORGPROTO_MESAFIX_VERSION).tar.bz2
XORGPROTO_MESAFIX_SITE = https://xorg.freedesktop.org/archive/individual/proto
XORGPROTO_MESAFIX_LICENSE = MIT
XORGPROTO_MESAFIX_LICENSE_FILES = \
	COPYING-applewmproto \
	COPYING-bigreqsproto \
	COPYING-compositeproto \
	COPYING-damageproto \
	COPYING-dmxproto \
	COPYING-dri2proto \
	COPYING-dri3proto \
	COPYING-evieproto \
	COPYING-fixesproto \
	COPYING-fontcacheproto \
	COPYING-fontsproto \
	COPYING-glproto \
	COPYING-inputproto \
	COPYING-kbproto \
	COPYING-lg3dproto \
	COPYING-pmproto \
	COPYING-presentproto \
	COPYING-printproto \
	COPYING-randrproto \
	COPYING-recordproto \
	COPYING-renderproto \
	COPYING-resourceproto \
	COPYING-scrnsaverproto \
	COPYING-trapproto \
	COPYING-videoproto \
	COPYING-windowswmproto \
	COPYING-x11proto \
	COPYING-xcmiscproto \
	COPYING-xextproto \
	COPYING-xf86bigfontproto \
	COPYING-xf86dgaproto \
	COPYING-xf86driproto \
	COPYING-xf86miscproto \
	COPYING-xf86rushproto \
	COPYING-xf86vidmodeproto \
	COPYING-xineramaproto
XORGPROTO_MESAFIX_INSTALL_STAGING = YES
XORGPROTO_MESAFIX_INSTALL_TARGET = NO
# xproxymngproto is needed by xfindproxy
XORGPROTO_MESAFIX_CONF_OPTS += --enable-legacy

$(eval $(autotools-package))
