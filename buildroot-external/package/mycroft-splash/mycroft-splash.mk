################################################################################
#
# mycroft-splash
#
################################################################################

MYCROFT_SPLASH_SOURCE = psplash-0a902f7cd875ccf018456451be369f05fa55f962.tar.gz
MYCROFT_SPLASH_SITE = http://git.yoctoproject.org/cgit/cgit.cgi/psplash/snapshot
MYCROFT_SPLASH_LICENSE = GPL-2.0+
MYCROFT_SPLASH_LICENSE_FILES = COPYING
MYCROFT_SPLASH_AUTORECONF = YES

define MYCROFT_SPLASH_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 644 $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-splash/mycroft-splash-start.service \
		$(TARGET_DIR)/usr/lib/systemd/system/mycroft-splash-start.service

	$(INSTALL) -D -m 644 $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-splash/mycroft-splash-quit.service \
		$(TARGET_DIR)/usr/lib/systemd/system/mycroft-splash-quit.service
endef

define MYCROFT_SPLASH_CHANGE_IMAGE
	cp $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-splash/psplash-colors.h $(@D)
	cp $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-splash/psplash-config.h $(@D)
	cp $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-splash/base-images/* $(@D)/base-images/
endef

MYCROFT_SPLASH_PRE_CONFIGURE_HOOKS += MYCROFT_SPLASH_CHANGE_IMAGE

$(eval $(autotools-package))
