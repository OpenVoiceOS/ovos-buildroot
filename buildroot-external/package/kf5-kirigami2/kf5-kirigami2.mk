################################################################################
#
# kf5-kirigami2
#
################################################################################

KF5_KIRIGAMI2_VERSION = $(KF5_VERSION)
KF5_KIRIGAMI2_SITE = $(KF5_SITE)
KF5_KIRIGAMI2_SOURCE = kirigami2-$(KF5_KIRIGAMI2_VERSION).tar.xz
KF5_KIRIGAMI2_LICENSE = BSD-3-Clause
KF5_KIRIGAMI2_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KIRIGAMI2_DEPENDENCIES = host-pkgconf
KF5_KIRIGAMI2_INSTALL_STAGING = YES
KF5_KIRIGAMI2_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
