################################################################################
#
# kf5-kjobwidgets
#
################################################################################

KF5_KJOBWIDGETS_VERSION = $(KF5_VERSION)
KF5_KJOBWIDGETS_SITE = $(KF5_SITE)
KF5_KJOBWIDGETS_SOURCE = kjobwidgets-$(KF5_KJOBWIDGETS_VERSION).tar.xz
KF5_KJOBWIDGETS_LICENSE = BSD-3-Clause
KF5_KJOBWIDGETS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KJOBWIDGETS_DEPENDENCIES = host-pkgconf
KF5_KJOBWIDGETS_INSTALL_STAGING = YES
KF5_KJOBWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
