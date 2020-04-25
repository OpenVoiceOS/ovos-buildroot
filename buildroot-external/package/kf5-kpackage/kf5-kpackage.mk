################################################################################
#
# kf5-kpackage
#
################################################################################

KF5_KPACKAGE_VERSION = $(KF5_VERSION)
KF5_KPACKAGE_SITE = $(KF5_SITE)
KF5_KPACKAGE_SOURCE = kpackage-$(KF5_KPACKAGE_VERSION).tar.xz
KF5_KPACKAGE_LICENSE = BSD-3-Clause
KF5_KPACKAGE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KPACKAGE_DEPENDENCIES = host-pkgconf
KF5_KPACKAGE_INSTALL_STAGING = YES
KF5_KPACKAGE_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
