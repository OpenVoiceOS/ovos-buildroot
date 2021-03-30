################################################################################
#
# btspeaker
#
################################################################################

BTSPEAKER_VERSION = 0.1.0
BTSPEAKER_SITE = $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/btspeaker
BTSPEAKER_SITE_METHOD = local
BTSPEAKER_LICENSE = Apache License 2.0
BTSPEAKER_LICENSE_FILES = LICENSE

define BTSPEAKER_BUILD_CMDS
	curl -L -o $(@D)/BCM43430A1.hcd https://raw.githubusercontent.com/RPi-Distro/bluez-firmware/e7fd166981ab4bb9a36c2d1500205a078a35714d/broadcom/BCM43430A1.hcd
	curl -L -o $(@D)/BCM4345C0.hcd https://raw.githubusercontent.com/RPi-Distro/bluez-firmware/e7fd166981ab4bb9a36c2d1500205a078a35714d/broadcom/BCM4345C0.hcd
	curl -L -o $(@D)/btuart https://raw.githubusercontent.com/RPi-Distro/pi-bluetooth/6f6386e91e33966d3c4a3cfee72d61e14c6a11ef/usr/bin/btuart
	curl -L -o $(@D)/bthelper https://raw.githubusercontent.com/RPi-Distro/pi-bluetooth/6f6386e91e33966d3c4a3cfee72d61e14c6a11ef/usr/bin/bthelper
	curl -L -o $(@D)/90-pi-bluetooth.rules https://raw.githubusercontent.com/RPi-Distro/pi-bluetooth/6f6386e91e33966d3c4a3cfee72d61e14c6a11ef/lib/udev/rules.d/90-pi-bluetooth.rules

	patch $(@D)/btuart $(@D)/0001-btuart-reduced-baud-rate-rpi3b.patch
endef

define BTSPEAKER_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 644 $(@D)/btspeaker.service \
		$(TARGET_DIR)/usr/lib/systemd/system/btspeaker.service

	$(INSTALL) -D -m 644 $(@D)/brcm_bt.service \
                $(TARGET_DIR)/usr/lib/systemd/system/brcm_bt.service

	$(INSTALL) -D -m 644 $(@D)/bthelper@.service \
                $(TARGET_DIR)/usr/lib/systemd/system/bthelper@.service

	mkdir -p $(TARGET_DIR)/etc/bluetooth
	$(INSTALL) -D -m 644 $(@D)/main.conf \
		$(TARGET_DIR)/etc/bluetooth/main.conf
	 $(INSTALL) -D -m 600 $(@D)/pin.conf \
                $(TARGET_DIR)/etc/bluetooth/pin.conf

	$(INSTALL) -d $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/btuart $(TARGET_DIR)/usr/bin/
	$(INSTALL) -m 0755 $(@D)/bthelper $(TARGET_DIR)/usr/bin/

	$(INSTALL) -d $(TARGET_DIR)/lib/firmware/brcm
	$(INSTALL) -m 0644 $(@D)/*.hcd $(TARGET_DIR)/lib/firmware/brcm/

	$(INSTALL) -d $(TARGET_DIR)/usr/lib/udev/rules.d
	$(INSTALL) -m 0644 $(@D)/90-pi-bluetooth.rules $(TARGET_DIR)/usr/lib/udev/rules.d/
endef

$(eval $(generic-package))
