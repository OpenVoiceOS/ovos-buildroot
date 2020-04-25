################################################################################
#
# kf5-solid
#
################################################################################

KF5_SOLID_VERSION = $(KF5_VERSION)
KF5_SOLID_SITE = $(KF5_SITE)
KF5_SOLID_SOURCE = solid-$(KF5_SOLID_VERSION).tar.xz
KF5_SOLID_LICENSE = BSD-3-Clause
KF5_SOLID_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_SOLID_DEPENDENCIES = host-pkgconf
KF5_SOLID_INSTALL_STAGING = YES
KF5_SOLID_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
