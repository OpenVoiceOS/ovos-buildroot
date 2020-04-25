################################################################################
#
# kf5-sonnet
#
################################################################################

KF5_SONNET_VERSION = $(KF5_VERSION)
KF5_SONNET_SITE = $(KF5_SITE)
KF5_SONNET_SOURCE = sonnet-$(KF5_SONNET_VERSION).tar.xz
KF5_SONNET_LICENSE = BSD-3-Clause
KF5_SONNET_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_SONNET_DEPENDENCIES = host-pkgconf
KF5_SONNET_INSTALL_STAGING = YES
KF5_SONNET_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
