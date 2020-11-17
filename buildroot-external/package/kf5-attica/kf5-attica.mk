################################################################################
#
# kf5-attica
#
################################################################################

KF5_ATTICA_VERSION = $(KF5_VERSION)
KF5_ATTICA_SITE = $(KF5_SITE)
KF5_ATTICA_SOURCE = attica-$(KF5_ATTICA_VERSION).tar.xz
KF5_ATTICA_LICENSE = BSD-3-Clause
KF5_ATTICA_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_ATTICA_DEPENDENCIES = host-pkgconf
KF5_ATTICA_INSTALL_STAGING = YES
KF5_ATTICA_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
