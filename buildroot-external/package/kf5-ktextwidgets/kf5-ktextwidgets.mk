################################################################################
#
# kf5-ktextwidgets
#
################################################################################

KF5_KTEXTWIDGETS_VERSION = $(KF5_VERSION)
KF5_KTEXTWIDGETS_SITE = $(KF5_SITE)
KF5_KTEXTWIDGETS_SOURCE = ktextwidgets-$(KF5_KTEXTWIDGETS_VERSION).tar.xz
KF5_KTEXTWIDGETS_LICENSE = BSD-3-Clause
KF5_KTEXTWIDGETS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KTEXTWIDGETS_DEPENDENCIES = host-pkgconf kf5-sonnet
KF5_KTEXTWIDGETS_INSTALL_STAGING = YES
KF5_KTEXTWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KTEXTWIDGETS_CONF_OPTS = -DBUILD_DESIGNERPLUGIN=OFF

$(eval $(cmake-package))
