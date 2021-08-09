################################################################################
#
# mycroft-skill-ovos-pairing
#
################################################################################

MYCROFT_SKILL_OVOS_PAIRING_VERSION = b09758266bd7c90dd1629e41cb17d0f23b64b3c3
MYCROFT_SKILL_OVOS_PAIRING_SITE = git://github.com/OpenVoiceOS/skill-ovos-pairing
MYCROFT_SKILL_OVOS_PAIRING_SITE_METHOD = git
MYCROFT_SKILL_OVOS_PAIRING_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_PAIRING_DIRNAME = skill-ovos-pairing.openvoiceos

define MYCROFT_SKILL_OVOS_PAIRING_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_PAIRING_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_PAIRING_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_PAIRING_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_PAIRING_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_PAIRING_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_PAIRING_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_PAIRING_DIRNAME)
endef

$(eval $(generic-package))
