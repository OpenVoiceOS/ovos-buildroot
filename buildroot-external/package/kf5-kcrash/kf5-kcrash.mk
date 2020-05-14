################################################################################
#
# kf5-kcrash
#
################################################################################

KF5_KCRASH_VERSION = $(KF5_VERSION)
KF5_KCRASH_SITE = $(KF5_SITE)
KF5_KCRASH_SOURCE = kcrash-$(KF5_KCRASH_VERSION).tar.xz
KF5_KCRASH_LICENSE = BSD-3-Clause
KF5_KCRASH_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KCRASH_DEPENDENCIES = host-pkgconf
KF5_KCRASH_INSTALL_STAGING = YES
KF5_KCRASH_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
