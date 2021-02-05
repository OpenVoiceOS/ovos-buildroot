################################################################################
#
# respeaker
#
################################################################################

RESPEAKER_VERSION = 8cce4e8ffa77e1e2b89812e5e2ccf6cfbc1086cf
RESPEAKER_SITE = $(call github,respeaker,seeed-voicecard,$(RESPEAKER_VERSION))
RESPEAKER_LICENSE = GNU General Public License v3.0
RESPEAKER_DEPENDENCIES = rpi-firmware dtc

$(eval $(kernel-module))

define RESPEAKER_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/respeaker/seeed-voicecard.service \
		$(TARGET_DIR)/usr/lib/systemd/system/seeed-voicecard.service

	mkdir -p $(TARGET_DIR)/etc/voicecard
	$(INSTALL) -D -m 0644 $(@D)/*.state $(TARGET_DIR)/etc/voicecard

	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/respeaker/seeed-voicecard \
		$(TARGET_DIR)/usr/bin

        $(INSTALL) -D -m 0644 $(@D)/seeed-4mic-voicecard.dtbo $(BINARIES_DIR)/overlays/
        $(INSTALL) -D -m 0644 $(@D)/seeed-8mic-voicecard.dtbo $(BINARIES_DIR)/overlays/

	mkdir -p $(TARGET_DIR)/usr/share/pulseaudio/alsa-mixer/profile-sets/
	$(INSTALL) -D -m 0644 $(@D)/pulseaudio/pulse_config_4mic/seeed-voicecard.conf \
		$(TARGET_DIR)/usr/share/pulseaudio/alsa-mixer/profile-sets/seeed-voicecard-4mic.conf
	$(INSTALL) -D -m 0644 $(@D)/pulseaudio/pulse_config_6mic/seeed-voicecard.conf \
                $(TARGET_DIR)/usr/share/pulseaudio/alsa-mixer/profile-sets/seeed-voicecard-8mic.conf
	$(INSTALL) -D -m 0644 $(@D)/pulseaudio/91-seeedvoicecard.rules \
		$(TARGET_DIR)/etc/udev/rules.d/91-seeedvoicecard.rules

	$(INSTALL) -D -m 0644 $(@D)/pulseaudio/pulse_config_4mic/default.pa \
		$(TARGET_DIR)/etc/pulse/seeed-voicecard-4mic-default.pa
	$(INSTALL) -D -m 0644 $(@D)/pulseaudio/pulse_config_4mic/daemon.conf \
                $(TARGET_DIR)/etc/pulse/seeed-voicecard-4mic-daemon.conf
	$(INSTALL) -D -m 0644 $(@D)/pulseaudio/pulse_config_6mic/default.pa \
                $(TARGET_DIR)/etc/pulse/seeed-voicecard-8mic-default.pa
        $(INSTALL) -D -m 0644 $(@D)/pulseaudio/pulse_config_6mic/daemon.conf \
                $(TARGET_DIR)/etc/pulse/seeed-voicecard-8mic-daemon.conf
endef

$(eval $(generic-package))
