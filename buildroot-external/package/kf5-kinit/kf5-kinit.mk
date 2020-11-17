################################################################################
#
# kf5-kinit
#
################################################################################

KF5_KINIT_VERSION = $(KF5_VERSION)
KF5_KINIT_SITE = $(KF5_SITE)
KF5_KINIT_SOURCE = kinit-$(KF5_KINIT_VERSION).tar.xz
KF5_KINIT_LICENSE = BSD-3-Clause
KF5_KINIT_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KINIT_DEPENDENCIES = host-pkgconf
KF5_KINIT_INSTALL_STAGING = YES
KF5_KINIT_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
