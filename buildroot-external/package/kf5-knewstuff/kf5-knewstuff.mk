################################################################################
#
# kf5-knewstuff
#
################################################################################

KF5_KNEWSTUFF_VERSION = $(KF5_VERSION)
KF5_KNEWSTUFF_SITE = $(KF5_SITE)
KF5_KNEWSTUFF_SOURCE = knewstuff-$(KF5_KNEWSTUFF_VERSION).tar.xz
KF5_KNEWSTUFF_LICENSE = BSD-3-Clause
KF5_KNEWSTUFF_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KNEWSTUFF_DEPENDENCIES = host-pkgconf
KF5_KNEWSTUFF_INSTALL_STAGING = YES
KF5_KNEWSTUFF_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
