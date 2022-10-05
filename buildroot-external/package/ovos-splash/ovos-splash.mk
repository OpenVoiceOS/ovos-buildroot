################################################################################
#
# ovos-splash
#
################################################################################

OVOS_SPLASH_SOURCE = psplash-0a902f7cd875ccf018456451be369f05fa55f962.tar.gz
OVOS_SPLASH_SITE = http://git.yoctoproject.org/cgit/cgit.cgi/psplash/snapshot
OVOS_SPLASH_LICENSE = GPL-2.0+
OVOS_SPLASH_LICENSE_FILES = COPYING
OVOS_SPLASH_AUTORECONF = YES

ifeq ($(BR2_PACKAGE_SYSTEMD),y)
OVOS_SPLASH_DEPENDENCIES += systemd
OVOS_SPLASH_CONF_OPTS += --with-systemd
else
OVOS_SPLASH_CONF_OPTS += --without-systemd
endif

define OVOS_SPLASH_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-splash/ovos-splash-start.service \
		$(TARGET_DIR)/usr/lib/systemd/system/ovos-splash-start.service

	$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-splash/ovos-splash-quit.service \
		$(TARGET_DIR)/usr/lib/systemd/system/ovos-splash-quit.service

	$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-splash/ovos-splash-systemd.service \
                $(TARGET_DIR)/usr/lib/systemd/system/ovos-splash-systemd.service
endef

define OVOS_SPLASH_CHANGE_IMAGE
	cp $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-splash/psplash-colors.h $(@D)
	cp $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-splash/psplash-config.h $(@D)
	cp $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-splash/base-images/* $(@D)/base-images/
endef

OVOS_SPLASH_PRE_CONFIGURE_HOOKS += OVOS_SPLASH_CHANGE_IMAGE

$(eval $(autotools-package))
