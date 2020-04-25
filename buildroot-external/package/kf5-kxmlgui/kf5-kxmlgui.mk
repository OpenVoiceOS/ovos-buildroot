################################################################################
#
# kf5-kxmlgui
#
################################################################################

KF5_KXMLGUI_VERSION = $(KF5_VERSION)
KF5_KXMLGUI_SITE = $(KF5_SITE)
KF5_KXMLGUI_SOURCE = kxmlgui-$(KF5_KXMLGUI_VERSION).tar.xz
KF5_KXMLGUI_LICENSE = BSD-3-Clause
KF5_KXMLGUI_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KXMLGUI_DEPENDENCIES = host-pkgconf
KF5_KXMLGUI_INSTALL_STAGING = YES
KF5_KXMLGUI_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
