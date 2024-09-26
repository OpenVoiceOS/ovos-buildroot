################################################################################
#
# rpi-bluetooth
#
################################################################################

RPI_BLUETOOTH_VERSION = 23af66cff597c80523bf9581d7f75d387227f183
RPI_BLUETOOTH_SITE = $(call github,RPi-Distro,pi-bluetooth,$(RPI_BLUETOOTH_VERSION))
RPI_BLUETOOTH_LICENSE = BSD-3-Clause
RPI_BLUETOOTH_LICENSE_FILES = debian/copyright

define RPI_BLUETOOTH_INSTALL_TARGET_CMDS
	$(INSTALL) -d $(TARGET_DIR)/etc/systemd/system/ovos-hardware.target.wants
	$(INSTALL) -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/rpi-bluetooth/hciuart.service $(TARGET_DIR)/usr/lib/systemd/system/
	$(INSTALL) -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/rpi-bluetooth/hcidisable.service $(TARGET_DIR)/usr/lib/systemd/system/
	$(INSTALL) -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/rpi-bluetooth/bthelper@.service $(TARGET_DIR)/usr/lib/systemd/system/

	$(INSTALL) -d $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/usr/bin/btuart $(TARGET_DIR)/usr/bin/
	$(INSTALL) -m 0755 $(@D)/usr/bin/bthelper $(TARGET_DIR)/usr/bin/

	$(INSTALL) -d $(TARGET_DIR)/usr/lib/udev/rules.d
	$(INSTALL) -m 0644 $(@D)/lib/udev/rules.d/90-pi-bluetooth.rules $(TARGET_DIR)/usr/lib/udev/rules.d/
endef

$(eval $(generic-package))
