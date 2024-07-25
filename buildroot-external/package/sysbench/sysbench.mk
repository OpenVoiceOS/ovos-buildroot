################################################################################
#
# SYSBENCH
#
################################################################################

SYSBENCH_VERSION = 1.0.20
SYSBENCH_SITE = $(call github,akopytov,sysbench,$(SYSBENCH_VERSION))
SYSBENCH_LICENSE = GPL-2.0+
SYSBENCH_LICENSE_FILES = COPYING

SYSBENCH_AUTORECONF = YES

SYSBENCH_DEPENDENCIES += host-pkgconf ck luajit

SYSBENCH_CONF_OPTS += \
	--without-lib-prefix \
	--with-system-luajit \
	--with-system-ck

ifeq ($(BR2_PACKAGE_MYSQL), y)
SYSBENCH_DEPENDENCIES += mysql
SYSBENCH_CONF_OPTS += \
	--with-mysql \
	--with-mysql-includes=$(STAGING_DIR)/usr/include/mysql \
	--with-mysql-libs=$(STAGING_DIR)/usr/lib
else
SYSBENCH_CONF_OPTS += --without-mysql
endif

$(eval $(autotools-package))
