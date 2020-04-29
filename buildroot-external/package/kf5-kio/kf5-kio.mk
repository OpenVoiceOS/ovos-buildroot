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

KF5_KIO_DEPENDENCIES = host-pkgconf host-kf5-kcoreaddons kf5-kservice kf5-solid \
			kf5-kjobwidgets kf5-ktextwidgets
KF5_KIO_INSTALL_STAGING = YES
KF5_KIO_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KIO_CONF_OPTS = -DBUILD_DESIGNERPLUGIN=OFF
KF5_KIO_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/usr/lib/cmake"

define KF5_KIO_PRE_XDG_EXPORT
	# desktoptojson needs to find installed service type files
	export XDG_DATA_DIRS=${HOST_DIR}/usr/share:$XDG_DATA_DIRS
endef

KF5_KIO_PRE_BUILD_HOOKS += KF5_KIO_PRE_XDG_EXPORT

$(eval $(cmake-package))
