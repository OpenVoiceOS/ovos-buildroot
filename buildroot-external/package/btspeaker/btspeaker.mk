################################################################################
#
# btspeaker
#
################################################################################

BTSPEAKER_VERSION = 0.1.0
BTSPEAKER_SITE = $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/btspeaker
BTSPEAKER_SITE_METHOD = local
BTSPEAKER_LICENSE = Apache License 2.0
BTSPEAKER_LICENSE_FILES = LICENSE

define BTSPEAKER_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 644 $(@D)/btspeaker.service \
		$(TARGET_DIR)/usr/lib/systemd/system/btspeaker.service

	$(INSTALL) -D -m 644 $(@D)/brcm_bt.service \
                $(TARGET_DIR)/usr/lib/systemd/system/brcm_bt.service

	mkdir -p $(TARGET_DIR)/etc/bluetooth
	$(INSTALL) -D -m 644 $(@D)/main.conf \
		$(TARGET_DIR)/etc/bluetooth/main.conf
	 $(INSTALL) -D -m 600 $(@D)/pin.conf \
                $(TARGET_DIR)/etc/bluetooth/pin.conf
endef

$(eval $(generic-package))
