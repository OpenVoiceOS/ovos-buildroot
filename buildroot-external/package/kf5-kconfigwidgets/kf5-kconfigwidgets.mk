################################################################################
#
# kf5-kconfigwidgets
#
################################################################################

KF5_KCONFIGWIDGETS_VERSION = $(KF5_VERSION)
KF5_KCONFIGWIDGETS_SITE = $(KF5_SITE)
KF5_KCONFIGWIDGETS_SOURCE = kconfigwidgets-$(KF5_KCONFIGWIDGETS_VERSION).tar.xz
KF5_KCONFIGWIDGETS_LICENSE = BSD-3-Clause
KF5_KCONFIGWIDGETS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KCONFIGWIDGETS_DEPENDENCIES = host-pkgconf
KF5_KCONFIGWIDGETS_INSTALL_STAGING = YES
KF5_KCONFIGWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
