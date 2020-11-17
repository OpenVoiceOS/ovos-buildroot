################################################################################
#
# kf5-kdoctools
#
################################################################################

KF5_KDOCTOOLS_VERSION = $(KF5_VERSION)
KF5_KDOCTOOLS_SITE = $(KF5_SITE)
KF5_KDOCTOOLS_SOURCE = kdoctools-$(KF5_KDOCTOOLS_VERSION).tar.xz
KF5_KDOCTOOLS_LICENSE = BSD-3-Clause
KF5_KDOCTOOLS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDOCTOOLS_DEPENDENCIES = host-pkgconf docbook-xml docbook-xsl \
				kf5-karchive kf5-ki18n host-kf5-kdoctools
KF5_KDOCTOOLS_INSTALL_STAGING = YES
KF5_KDOCTOOLS_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KDOCTOOLS_CONF_OPTS += -DKF5_HOST_TOOLING=$(HOST_DIR)/lib/x86_64-linux-gnu/cmake
KF5_KDOCTOOLS_CONF_OPTS += -DMEINPROC5_EXECUTABLE=${HOST_DIR}/bin/meinproc5
KF5_KDOCTOOLS_CONF_OPTS += -DDOCBOOKL10NHELPER_EXECUTABLE=${HOST_DIR}/bin/docbookl10nhelper
KF5_KDOCTOOLS_CONF_OPTS += -DCHECKXML5_EXECUTABLE=${HOST_DIR}/bin/checkXML5

KF5_KDOCTOOLS_POST_INSTALL_STAGING_HOOKS += KF5_KDOCTOOLS_COPY_BINS

define KF5_KDOCTOOLS_COPY_BINS
	cp ${HOST_DIR}/bin/checkXML5 $(STAGING_DIR)/usr/bin
	cp ${HOST_DIR}/bin/meinproc5 $(STAGING_DIR)/usr/bin
endef

$(eval $(cmake-package))

HOST_KF5_KDOCTOOLS_DEPENDENCIES = host-kf5-extra-cmake-modules
HOST_KF5_KDOCTOOLS_CXXFLAGS = $(HOST_CXXFLAGS)
HOST_KF5_KDOCTOOLS_CONF_OPTS = -DCMAKE_CXX_FLAGS="$(HOST_KF5_KDOCTOOLS_CXXFLAGS)"
HOST_KF5_KDOCTOOLS_CONF_OPTS += -DINSTALL_INTERNAL_TOOLS=ON

define HOST_KF5_KDOCTOOLS_INSTALL_CMDS
	cp $(@D)/buildroot-build/bin/docbookl10nhelper $(HOST_DIR)/bin
	cp $(@D)/buildroot-build/bin/meinproc5 $(HOST_DIR)/bin
	cp $(@D)/buildroot-build/bin/checkXML5 $(HOST_DIR)/bin
endef

$(eval $(host-cmake-package))
