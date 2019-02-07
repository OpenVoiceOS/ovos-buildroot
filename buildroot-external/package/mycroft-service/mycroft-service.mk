################################################################################
#
# mycroft-service
#
################################################################################

MYCROFT_SERVICE_VERSION = 0.1.0
MYCROFT_SERVICE_SITE = $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-service
MYCROFT_SERVICE_SITE_METHOD = local
MYCROFT_SERVICE_LICENSE = Apache License 2.0
MYCROFT_SERVICE_LICENSE_FILES = LICENSE

define MYCROFT_SERVICE_USERS
	mycroft -1 mycroft -1 * /home/mycroft /bin/sh audio,pulse-access
endef

define MYCROFT_SERVICE_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 $(@D)/start-mycroft.sh $(TARGET_DIR)/usr/bin/
	$(INSTALL) -m 0755 $(@D)/stop-mycroft.sh $(TARGET_DIR)/usr/bin/
	$(INSTALL) -D -m 644 $(@D)/mycroft.service \
		$(TARGET_DIR)/usr/lib/systemd/system/mycroft.service
	mkdir -p $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	ln -fs ../../../../usr/lib/systemd/system/mycroft.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/mycroft.service
endef

$(eval $(generic-package))
