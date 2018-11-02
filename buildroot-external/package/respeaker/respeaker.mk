################################################################################
#
# respeaker
#
################################################################################

RESPEAKER_VERSION = be0812c70be29b0666a89f22a9d403cfb4c48fca
RESPEAKER_SITE = $(call github,respeaker,seeed-voicecard,$(RESPEAKER_VERSION))
RESPEAKER_LICENSE = GNU General Public License v3.0
RESPEAKER_DEPENDENCIES = rpi-firmware rpi-userland dtc

$(eval $(kernel-module))

define RESPEAKER_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/respeaker/S16respeaker_modules \
		$(TARGET_DIR)/etc/init.d/S16respeaker_modules
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/respeaker/S60seeed_voicecard \
                $(TARGET_DIR)/etc/init.d/S60seeed_voicecard

	mkdir -p $(TARGET_DIR)/etc/voicecard
	rm $(@D)/dkms.conf
	$(INSTALL) -D -m 0644 $(@D)/*.conf $(TARGET_DIR)/etc/voicecard
	$(INSTALL) -D -m 0644 $(@D)/*.state $(TARGET_DIR)/etc/voicecard
	$(INSTALL) -D -m 0755 $(@D)/seeed-voicecard $(TARGET_DIR)/usr/bin

	$(INSTALL) -D -m 0644 $(@D)/seeed-2mic-voicecard.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/
        $(INSTALL) -D -m 0644 $(@D)/seeed-4mic-voicecard.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/
        $(INSTALL) -D -m 0644 $(@D)/seeed-8mic-voicecard.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/
endef

$(eval $(generic-package))
