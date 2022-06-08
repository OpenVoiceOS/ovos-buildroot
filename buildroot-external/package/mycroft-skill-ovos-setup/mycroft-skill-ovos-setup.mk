################################################################################
#
# mycroft-skill-ovos-setup
#
################################################################################

MYCROFT_SKILL_OVOS_SETUP_VERSION = 0ebb4d4ce19908cf2a337a1ef3f7d4e428f43107
MYCROFT_SKILL_OVOS_SETUP_SITE = https://github.com/OpenVoiceOS/skill-ovos-setup
MYCROFT_SKILL_OVOS_SETUP_SITE_METHOD = git
MYCROFT_SKILL_OVOS_SETUP_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_SETUP_DIRNAME = skill-ovos-setup.openvoiceos

define MYCROFT_SKILL_OVOS_SETUP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_SETUP_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_SETUP_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_SETUP_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_SETUP_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_SETUP_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_SETUP_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_SETUP_DIRNAME)
endef

$(eval $(generic-package))
