################################################################################
#
# kf5-kded
#
################################################################################

KF5_KDED_VERSION = $(KF5_VERSION)
KF5_KDED_SITE = $(KF5_SITE)
KF5_KDED_SOURCE = kded-$(KF5_KDED_VERSION).tar.xz
KF5_KDED_LICENSE = BSD-3-Clause
KF5_KDED_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDED_DEPENDENCIES = host-pkgconf
KF5_KDED_INSTALL_STAGING = YES
KF5_KDED_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
