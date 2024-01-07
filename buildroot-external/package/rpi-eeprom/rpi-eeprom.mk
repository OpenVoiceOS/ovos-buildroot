#############################################################
#
# rpi-eeprom
#
#############################################################
RPI_EEPROM_VERSION = 9e0bffb2916d6f31ae454a365bb1b563ee14bf97
RPI_EEPROM_SITE = $(call github,raspberrypi,rpi-eeprom,$(RPI_EEPROM_VERSION))
RPI_EEPROM_LICENSE = BSD-3-Clause
RPI_EEPROM_LICENSE_FILES = LICENSE
RPI_EEPROM_INSTALL_IMAGES = YES

# Conditional firmware path based on kernel defconfig
ifeq ($(BR2_LINUX_KERNEL_DEFCONFIG), "bcm2711") # Raspberry Pi 3/4
    RPI_EEPROM_FIRMWARE_PATH = firmware-2711/stable/pieeprom-2023-05-11.bin
else ifeq ($(BR2_LINUX_KERNEL_DEFCONFIG), "bcm2712") # Raspberry Pi 5
    RPI_EEPROM_FIRMWARE_PATH = firmware-2712/stable/pieeprom-2024-01-05.bin
else
    $(error Unsupported Raspberry Pi model for RPI_EEPROM_FIRMWARE_PATH)
endif

define RPI_EEPROM_BUILD_CMDS
	$(@D)/rpi-eeprom-config $(@D)/$(RPI_EEPROM_FIRMWARE_PATH) --out $(@D)/default.conf
	(cat $(@D)/default.conf | grep -v ^$$; echo HDMI_DELAY=0) > $(@D)/boot.conf
	$(@D)/rpi-eeprom-config $(@D)/$(RPI_EEPROM_FIRMWARE_PATH) --config $(@D)/boot.conf --out $(@D)/pieeprom.upd
	sha256sum $(@D)/pieeprom.upd | awk '{ print $$1 }' > $(@D)/pieeprom.sig
	echo "ts: $$(date -u +%s)" >> $(@D)/pieeprom.sig
endef

define RPI_EEPROM_INSTALL_IMAGES_CMDS
	$(INSTALL) -D -m 0644 $(@D)/pieeprom.sig $(BINARIES_DIR)/rpi-eeprom/pieeprom.sig
	$(INSTALL) -D -m 0644 $(@D)/pieeprom.upd $(BINARIES_DIR)/rpi-eeprom/pieeprom.upd
endef

$(eval $(generic-package))
