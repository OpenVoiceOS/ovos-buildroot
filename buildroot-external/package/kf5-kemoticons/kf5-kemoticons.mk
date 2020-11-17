################################################################################
#
# kf5-kemoticons
#
################################################################################

KF5_KEMOTICONS_VERSION = $(KF5_VERSION)
KF5_KEMOTICONS_SITE = $(KF5_SITE)
KF5_KEMOTICONS_SOURCE = kemoticons-$(KF5_KEMOTICONS_VERSION).tar.xz
KF5_KEMOTICONS_LICENSE = BSD-3-Clause
KF5_KEMOTICONS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KEMOTICONS_DEPENDENCIES = host-pkgconf
KF5_KEMOTICONS_INSTALL_STAGING = YES
KF5_KEMOTICONS_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KEMOTICONS_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
