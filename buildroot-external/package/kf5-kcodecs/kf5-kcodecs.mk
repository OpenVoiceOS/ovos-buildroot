################################################################################
#
# kf5-kcodecs
#
################################################################################

KF5_KCODECS_VERSION = $(KF5_VERSION)
KF5_KCODECS_SITE = $(KF5_SITE)
KF5_KCODECS_SOURCE = kcodecs-$(KF5_KCODECS_VERSION).tar.xz
KF5_KCODECS_LICENSE = BSD-3-Clause
KF5_KCODECS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KCODECS_DEPENDENCIES = host-pkgconf
KF5_KCODECS_INSTALL_STAGING = YES
KF5_KCODECS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
