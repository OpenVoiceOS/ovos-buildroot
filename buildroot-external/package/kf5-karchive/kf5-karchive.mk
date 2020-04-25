################################################################################
#
# kf5-karchive
#
################################################################################

KF5_KARCHIVE_VERSION = $(KF5_VERSION)
KF5_KARCHIVE_SITE = $(KF5_SITE)
KF5_KARCHIVE_SOURCE = karchive-$(KF5_KARCHIVE_VERSION).tar.xz
KF5_KARCHIVE_LICENSE = BSD-3-Clause
KF5_KARCHIVE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KARCHIVE_DEPENDENCIES = host-pkgconf
KF5_KARCHIVE_INSTALL_STAGING = YES
KF5_KARCHIVE_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
