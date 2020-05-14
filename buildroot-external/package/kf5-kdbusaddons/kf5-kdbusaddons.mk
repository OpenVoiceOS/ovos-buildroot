################################################################################
#
# kf5-kdbusaddons
#
################################################################################

KF5_KDBUSADDONS_VERSION = $(KF5_VERSION)
KF5_KDBUSADDONS_SITE = $(KF5_SITE)
KF5_KDBUSADDONS_SOURCE = kdbusaddons-$(KF5_KDBUSADDONS_VERSION).tar.xz
KF5_KDBUSADDONS_LICENSE = BSD-3-Clause
KF5_KDBUSADDONS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDBUSADDONS_DEPENDENCIES = host-pkgconf
KF5_KDBUSADDONS_INSTALL_STAGING = YES
KF5_KDBUSADDONS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
