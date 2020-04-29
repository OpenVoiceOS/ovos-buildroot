################################################################################
#
# kf5-kdeclarative
#
################################################################################

KF5_KDECLARATIVE_VERSION = $(KF5_VERSION)
KF5_KDECLARATIVE_SITE = $(KF5_SITE)
KF5_KDECLARATIVE_SOURCE = kdeclarative-$(KF5_KDECLARATIVE_VERSION).tar.xz
KF5_KDECLARATIVE_LICENSE = BSD-3-Clause
KF5_KDECLARATIVE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDECLARATIVE_DEPENDENCIES = host-pkgconf kf5-kio
KF5_KDECLARATIVE_INSTALL_STAGING = YES
KF5_KDECLARATIVE_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
