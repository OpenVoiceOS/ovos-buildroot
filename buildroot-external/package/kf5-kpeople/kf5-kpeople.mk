################################################################################
#
# kf5-kpeople
#
################################################################################

KF5_KPEOPLE_VERSION = $(KF5_VERSION)
KF5_KPEOPLE_SITE = $(KF5_SITE)
KF5_KPEOPLE_SOURCE = kpeople-$(KF5_KPEOPLE_VERSION).tar.xz
KF5_KPEOPLE_LICENSE = BSD-3-Clause
KF5_KPEOPLE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KPEOPLE_DEPENDENCIES = host-pkgconf
KF5_KPEOPLE_INSTALL_STAGING = YES
KF5_KPEOPLE_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
