################################################################################
#
# mycroft-splash
#
################################################################################

MYCROFT_SPLASH_VERSION = 0.1.0
MYCROFT_SPLASH_SITE = $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-splash
MYCROFT_SPLASH_SITE_METHOD = local
MYCROFT_SPLASH_LICENSE = Apache License 2.0
MYCROFT_SPLASH_LICENSE_FILES = LICENSE

define MYCROFT_SPLASH_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 644 $(@D)/boot-splashscreen.service \
		$(TARGET_DIR)/usr/lib/systemd/system/boot-splashscreen.service
	mkdir -p $(TARGET_DIR)/etc/systemd/system/basic.target.wants
	ln -fs ../../../../usr/lib/systemd/system/boot-splashscreen.service \
		$(TARGET_DIR)/etc/systemd/system/basic.target.wants/boot-splashscreen.service

	$(INSTALL) -D -m 644 $(@D)/halt-splashscreen.service \
                $(TARGET_DIR)/usr/lib/systemd/system/halt-splashscreen.service
        mkdir -p $(TARGET_DIR)/etc/systemd/system/halt.target.wants
        ln -fs ../../../../usr/lib/systemd/system/halt-splashscreen.service \
                $(TARGET_DIR)/etc/systemd/system/halt.target.wants/halt-splashscreen.service
	mkdir -p $(TARGET_DIR)/etc/systemd/system/poweroff.target.wants
        ln -fs ../../../../usr/lib/systemd/system/halt-splashscreen.service \
                $(TARGET_DIR)/etc/systemd/system/poweroff.target.wants/halt-splashscreen.service

	$(INSTALL) -D -m 644 $(@D)/off-splashscreen.service \
                $(TARGET_DIR)/usr/lib/systemd/system/off-splashscreen.service
        mkdir -p $(TARGET_DIR)/etc/systemd/system/shutdown.target.wants
        ln -fs ../../../../usr/lib/systemd/system/off-splashscreen.service \
                $(TARGET_DIR)/etc/systemd/system/shutdown.target.wants/off-splashscreen.service
endef

$(eval $(generic-package))
