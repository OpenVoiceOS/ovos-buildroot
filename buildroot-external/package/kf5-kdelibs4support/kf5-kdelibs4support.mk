################################################################################
#
# kf5-kdelibs4support
#
################################################################################

KF5_KDELIBS4SUPPORT_VERSION = $(KF5_VERSION)
KF5_KDELIBS4SUPPORT_SITE = $(KF5_SITE)/portingAids
KF5_KDELIBS4SUPPORT_SOURCE = kdelibs4support-$(KF5_KDELIBS4SUPPORT_VERSION).tar.xz
KF5_KDELIBS4SUPPORT_LICENSE = BSD-3-Clause
KF5_KDELIBS4SUPPORT_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDELIBS4SUPPORT_DEPENDENCIES = host-pkgconf qt5base qt5svg \
				   kf5-kdoctools \
				   kf5-kcompletion \
				   kf5-kconfigwidgets \
				   kf5-kcrash \
				   kf5-kded \
			 	   kf5-kdesignerplugin \
				   host-kf5-kdesignerplugin \
				   kf5-kemoticons \
				   kf5-kglobalaccel \
				   kf5-kiconthemes \
				   kf5-kio \
				   host-kf5-kcoreaddons \
				   host-kf5-kconfig \
				   host-kf5-kauth \
				   kf5-knotifications \
				   kf5-kparts \
				   kf5-kunitconversion

KF5_KDELIBS4SUPPORT_INSTALL_STAGING = YES
KF5_KDELIBS4SUPPORT_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KDELIBS4SUPPORT_CONF_OPTS = -DHAVE_GOOD_GETADDRINFO=ON

$(eval $(cmake-package))
