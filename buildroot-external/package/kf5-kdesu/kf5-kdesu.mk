################################################################################
#
# kf5-kdesu
#
################################################################################

KF5_KDESU_VERSION = $(KF5_VERSION)
KF5_KDESU_SITE = $(KF5_SITE)
KF5_KDESU_SOURCE = kdesu-$(KF5_KDESU_VERSION).tar.xz
KF5_KDESU_LICENSE = BSD-3-Clause
KF5_KDESU_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDESU_DEPENDENCIES = host-pkgconf kf5-kpty
KF5_KDESU_INSTALL_STAGING = YES
KF5_KDESU_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
