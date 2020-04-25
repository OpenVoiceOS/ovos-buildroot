################################################################################
#
# kf5-kdoctools
#
################################################################################

KF5_KDOCTOOLS_VERSION = $(KF5_VERSION)
KF5_KDOCTOOLS_SITE = $(KF5_SITE)
KF5_KDOCTOOLS_SOURCE = kdoctools-$(KF5_KDOCTOOLS_VERSION).tar.xz
KF5_KDOCTOOLS_LICENSE = BSD-3-Clause
KF5_KDOCTOOLS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDOCTOOLS_DEPENDENCIES = host-pkgconf
KF5_KDOCTOOLS_INSTALL_STAGING = YES
KF5_KDOCTOOLS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
