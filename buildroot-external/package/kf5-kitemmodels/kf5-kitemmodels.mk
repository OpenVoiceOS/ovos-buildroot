################################################################################
#
# kf5-kitemmodels
#
################################################################################

KF5_KITEMMODELS_VERSION = $(KF5_VERSION)
KF5_KITEMMODELS_SITE = $(KF5_SITE)
KF5_KITEMMODELS_SOURCE = kitemmodels-$(KF5_KITEMMODELS_VERSION).tar.xz
KF5_KITEMMODELS_LICENSE = BSD-3-Clause
KF5_KITEMMODELS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KITEMMODELS_DEPENDENCIES = host-pkgconf
KF5_KITEMMODELS_INSTALL_STAGING = YES
KF5_KITEMMODELS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
