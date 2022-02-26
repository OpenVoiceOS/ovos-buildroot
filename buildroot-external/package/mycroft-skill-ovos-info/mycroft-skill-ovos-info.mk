################################################################################
#
# mycroft-skill-ovos-info
#
################################################################################

MYCROFT_SKILL_OVOS_INFO_VERSION = acab00e38d5492aca13b2072114f630791b5ee01
MYCROFT_SKILL_OVOS_INFO_SITE = https://github.com/OpenVoiceOS/ovos-skills-info
MYCROFT_SKILL_OVOS_INFO_SITE_METHOD = git
MYCROFT_SKILL_OVOS_INFO_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_INFO_DIRNAME = ovos-skills-info.openvoiceos

define MYCROFT_SKILL_OVOS_INFO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_INFO_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_INFO_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_INFO_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_INFO_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_INFO_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_INFO_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_INFO_DIRNAME)
endef

$(eval $(generic-package))
