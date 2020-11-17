################################################################################
#
# kf5-kactivities-stats
#
################################################################################

KF5_KACTIVITIES_STATS_VERSION = $(KF5_VERSION)
KF5_KACTIVITIES_STATS_SITE = $(KF5_SITE)
KF5_KACTIVITIES_STATS_SOURCE = kactivities-stats-$(KF5_KACTIVITIES_STATS_VERSION).tar.xz
KF5_KACTIVITIES_STATS_LICENSE = BSD-3-Clause
KF5_KACTIVITIES_STATS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KACTIVITIES_STATS_DEPENDENCIES = host-pkgconf kf5-kconfig kf5-kactivities
KF5_KACTIVITIES_STATS_INSTALL_STAGING = YES
KF5_KACTIVITIES_STATS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
