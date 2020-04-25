################################################################################
#
# kf5-kio
#
################################################################################

KF5_KIO_VERSION = $(KF5_VERSION)
KF5_KIO_SITE = $(KF5_SITE)
KF5_KIO_SOURCE = kio-$(KF5_KIO_VERSION).tar.xz
KF5_KIO_LICENSE = BSD-3-Clause
KF5_KIO_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KIO_DEPENDENCIES = host-pkgconf
KF5_KIO_INSTALL_STAGING = YES
KF5_KIO_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
