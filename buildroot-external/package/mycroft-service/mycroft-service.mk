################################################################################
#
# mycroft-service
#
################################################################################

MYCROFT_SERVICE_VERSION = 0.1.0
MYCROFT_SERVICE_SITE = $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/mycroft-service
MYCROFT_SERVICE_SITE_METHOD = local
MYCROFT_SERVICE_LICENSE = Apache License 2.0
MYCROFT_SERVICE_LICENSE_FILES = LICENSE

define MYCROFT_SERVICE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/home/mycroft/.local/share/systemd
	$(INSTALL) -m 0755 $(@D)/mycroft-systemd_audio.py \
		$(TARGET_DIR)/home/mycroft/.local/share/systemd/mycroft-systemd_audio.py
	$(INSTALL) -m 0755 $(@D)/mycroft-systemd_enclosure.py \
                $(TARGET_DIR)/home/mycroft/.local/share/systemd/mycroft-systemd_enclosure.py
	$(INSTALL) -m 0755 $(@D)/mycroft-systemd_messagebus.py \
                $(TARGET_DIR)/home/mycroft/.local/share/systemd/mycroft-systemd_messagebus.py
	$(INSTALL) -m 0755 $(@D)/mycroft-systemd_skills.py \
                $(TARGET_DIR)/home/mycroft/.local/share/systemd/mycroft-systemd_skills.py
	$(INSTALL) -m 0755 $(@D)/mycroft-systemd_voice.py \
                $(TARGET_DIR)/home/mycroft/.local/share/systemd/mycroft-systemd_voice.py
	$(INSTALL) -m 0755 $(@D)/mycroft-systemd_gui.py \
                $(TARGET_DIR)/home/mycroft/.local/share/systemd/mycroft-systemd_gui.py

	$(INSTALL) -D -m 644 $(@D)/mycroft.service \
		$(TARGET_DIR)/usr/lib/systemd/system/mycroft.service
	$(INSTALL) -D -m 644 $(@D)/mycroft-messagebus.service \
                $(TARGET_DIR)/usr/lib/systemd/system/mycroft-messagebus.service
	$(INSTALL) -D -m 644 $(@D)/mycroft-audio.service \
                $(TARGET_DIR)/usr/lib/systemd/system/mycroft-audio.service
	$(INSTALL) -D -m 644 $(@D)/mycroft-voice.service \
                $(TARGET_DIR)/usr/lib/systemd/system/mycroft-voice.service
	$(INSTALL) -D -m 644 $(@D)/mycroft-enclosure.service \
                $(TARGET_DIR)/usr/lib/systemd/system/mycroft-enclosure.service
	$(INSTALL) -D -m 644 $(@D)/mycroft-skills.service \
                $(TARGET_DIR)/usr/lib/systemd/system/mycroft-skills.service
	$(INSTALL) -D -m 644 $(@D)/mycroft-gui.service \
                $(TARGET_DIR)/usr/lib/systemd/system/mycroft-gui.service
	$(INSTALL) -D -m 644 $(@D)/mycroft-enclosure-gui.service \
                $(TARGET_DIR)/usr/lib/systemd/system/mycroft-enclosure-gui.service
endef

$(eval $(generic-package))
