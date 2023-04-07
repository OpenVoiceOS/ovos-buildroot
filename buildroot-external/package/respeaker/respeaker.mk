################################################################################
#
# respeaker
#
################################################################################

RESPEAKER_VERSION = 977a7ff321b1949e8ce4555fb0e3677fd47d46b2
RESPEAKER_SITE = $(call github,HinTak,seeed-voicecard,$(RESPEAKER_VERSION))
RESPEAKER_LICENSE = GNU General Public License v3.0
RESPEAKER_DEPENDENCIES = rpi-firmware dtc

$(eval $(kernel-module))

define RESPEAKER_INSTALL_TARGET_CMDS

	mkdir -p $(TARGET_DIR)/etc/voicecard
	$(INSTALL) -D -m 0644 $(@D)/*.state $(TARGET_DIR)/etc/voicecard

	mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
	$(INSTALL) -D -m 0644 $(@D)/seeed-2mic-voicecard.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/
        $(INSTALL) -D -m 0644 $(@D)/seeed-4mic-voicecard.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/
        $(INSTALL) -D -m 0644 $(@D)/seeed-8mic-voicecard.dtbo $(BINARIES_DIR)/rpi-firmware/overlays/

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
