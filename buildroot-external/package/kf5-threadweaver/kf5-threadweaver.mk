################################################################################
#
# kf5-threadweaver
#
################################################################################

KF5_THREADWEAVER_VERSION = $(KF5_VERSION)
KF5_THREADWEAVER_SITE = $(KF5_SITE)
KF5_THREADWEAVER_SOURCE = threadweaver-$(KF5_THREADWEAVER_VERSION).tar.xz
KF5_THREADWEAVER_LICENSE = BSD-3-Clause
KF5_THREADWEAVER_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_THREADWEAVER_DEPENDENCIES = host-pkgconf
KF5_THREADWEAVER_INSTALL_STAGING = YES
KF5_THREADWEAVER_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
