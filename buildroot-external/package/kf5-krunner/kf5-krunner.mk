################################################################################
#
# kf5-krunner
#
################################################################################

KF5_KRUNNER_VERSION = $(KF5_VERSION)
KF5_KRUNNER_SITE = $(KF5_SITE)
KF5_KRUNNER_SOURCE = krunner-$(KF5_KRUNNER_VERSION).tar.xz
KF5_KRUNNER_LICENSE = BSD-3-Clause
KF5_KRUNNER_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KRUNNER_DEPENDENCIES = host-pkgconf kf5-threadweaver
KF5_KRUNNER_INSTALL_STAGING = YES
KF5_KRUNNER_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
