################################################################################
#
# kf5-prison
#
################################################################################

KF5_PRISON_VERSION = $(KF5_VERSION)
KF5_PRISON_SITE = $(KF5_SITE)
KF5_PRISON_SOURCE = prison-$(KF5_PRISON_VERSION).tar.xz
KF5_PRISON_LICENSE = BSD-3-Clause
KF5_PRISON_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PRISON_DEPENDENCIES = host-pkgconf libqrencode
KF5_PRISON_INSTALL_STAGING = YES
KF5_PRISON_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
