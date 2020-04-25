################################################################################
#
# kf5-kbookmarks
#
################################################################################

KF5_KBOOKMARKS_VERSION = $(KF5_VERSION)
KF5_KBOOKMARKS_SITE = $(KF5_SITE)
KF5_KBOOKMARKS_SOURCE = kbookmarks-$(KF5_KBOOKMARKS_VERSION).tar.xz
KF5_KBOOKMARKS_LICENSE = BSD-3-Clause
KF5_KBOOKMARKS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KBOOKMARKS_DEPENDENCIES = host-pkgconf
KF5_KBOOKMARKS_INSTALL_STAGING = YES
KF5_KBOOKMARKS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
