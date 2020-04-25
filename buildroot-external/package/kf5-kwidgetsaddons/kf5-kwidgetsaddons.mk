################################################################################
#
# kf5-kwidgetsaddons
#
################################################################################

KF5_KWIDGETSADDONS_VERSION = $(KF5_VERSION)
KF5_KWIDGETSADDONS_SITE = $(KF5_SITE)
KF5_KWIDGETSADDONS_SOURCE = kwidgetsaddons-$(KF5_KWIDGETSADDONS_VERSION).tar.xz
KF5_KWIDGETSADDONS_LICENSE = BSD-3-Clause
KF5_KWIDGETSADDONS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KWIDGETSADDONS_DEPENDENCIES = host-pkgconf
KF5_KWIDGETSADDONS_INSTALL_STAGING = YES
KF5_KWIDGETSADDONS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
