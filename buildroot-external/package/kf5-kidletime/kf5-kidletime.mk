################################################################################
#
# kf5-kidletime
#
################################################################################

KF5_KIDLETIME_VERSION = $(KF5_VERSION)
KF5_KIDLETIME_SITE = $(KF5_SITE)
KF5_KIDLETIME_SOURCE = kidletime-$(KF5_KIDLETIME_VERSION).tar.xz
KF5_KIDLETIME_LICENSE = BSD-3-Clause
KF5_KIDLETIME_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KIDLETIME_DEPENDENCIES = host-pkgconf
KF5_KIDLETIME_INSTALL_STAGING = YES
KF5_KIDLETIME_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
