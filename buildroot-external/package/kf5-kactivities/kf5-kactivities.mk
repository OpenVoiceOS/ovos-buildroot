################################################################################
#
# kf5-kactivities
#
################################################################################

KF5_KACTIVITIES_VERSION = $(KF5_VERSION)
KF5_KACTIVITIES_SITE = $(KF5_SITE)
KF5_KACTIVITIES_SOURCE = kactivities-$(KF5_KACTIVITIES_VERSION).tar.xz
KF5_KACTIVITIES_LICENSE = BSD-3-Clause
KF5_KACTIVITIES_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KACTIVITIES_DEPENDENCIES = host-pkgconf
KF5_KACTIVITIES_INSTALL_STAGING = YES
KF5_KACTIVITIES_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
