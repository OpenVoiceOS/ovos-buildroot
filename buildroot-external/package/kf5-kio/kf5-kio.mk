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

KF5_KIO_DEPENDENCIES = host-pkgconf kf5-kservice kf5-solid \
			kf5-kjobwidgets kf5-ktextwidgets \
			kf5-knotifications kf5-kded #host-kf5-desktoptojson
			#host-kf5-kcoreaddons

KF5_KIO_INSTALL_STAGING = YES
KF5_KIO_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KIO_CONF_OPTS = -DBUILD_DESIGNERPLUGIN=OFF
#KF5_KIO_CONF_OPTS += -DDESKTOPTOJSON_EXECUTABLE=/usr/bin/desktoptojson

$(eval $(cmake-package))
