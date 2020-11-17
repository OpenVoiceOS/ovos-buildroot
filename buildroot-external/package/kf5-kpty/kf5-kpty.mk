################################################################################
#
# kf5-kpty
#
################################################################################

KF5_KPTY_VERSION = $(KF5_VERSION)
KF5_KPTY_SITE = $(KF5_SITE)
KF5_KPTY_SOURCE = kpty-$(KF5_KPTY_VERSION).tar.xz
KF5_KPTY_LICENSE = BSD-3-Clause
KF5_KPTY_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KPTY_DEPENDENCIES = host-pkgconf
KF5_KPTY_INSTALL_STAGING = YES
KF5_KPTY_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
