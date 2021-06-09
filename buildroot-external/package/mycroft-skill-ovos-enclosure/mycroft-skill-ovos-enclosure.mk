################################################################################
#
# mycroft-skill-ovos-enclosure
#
################################################################################

MYCROFT_SKILL_OVOS_ENCLOSURE_VERSION = 96f6b24faf146fb8811f0fdf753748991d414dcd
MYCROFT_SKILL_OVOS_ENCLOSURE_SITE = git://github.com/OpenVoiceOS/skill-ovos-enclosure
MYCROFT_SKILL_OVOS_ENCLOSURE_SITE_METHOD = git
MYCROFT_SKILL_OVOS_ENCLOSURE_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_ENCLOSURE_DIRNAME = skill-ovos-enclosure.openvoiceos

define MYCROFT_SKILL_OVOS_ENCLOSURE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_ENCLOSURE_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_ENCLOSURE_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_ENCLOSURE_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_ENCLOSURE_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_ENCLOSURE_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_ENCLOSURE_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_ENCLOSURE_DIRNAME)
endef

$(eval $(generic-package))
