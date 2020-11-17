################################################################################
#
# kf5-kwallet
#
################################################################################

KF5_KWALLET_VERSION = $(KF5_VERSION)
KF5_KWALLET_SITE = $(KF5_SITE)
KF5_KWALLET_SOURCE = kwallet-$(KF5_KWALLET_VERSION).tar.xz
KF5_KWALLET_LICENSE = BSD-3-Clause
KF5_KWALLET_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KWALLET_DEPENDENCIES = host-pkgconf
KF5_KWALLET_INSTALL_STAGING = YES
KF5_KWALLET_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
