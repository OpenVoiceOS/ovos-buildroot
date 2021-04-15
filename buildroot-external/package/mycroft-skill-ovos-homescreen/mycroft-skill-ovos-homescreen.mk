################################################################################
#
# mycroft-skill-ovos-homescreen
#
################################################################################

MYCROFT_SKILL_OVOS_HOMESCREEN_VERSION = c68f2ac63b5fc112578f89f5307a2a7b3db2da9a
MYCROFT_SKILL_OVOS_HOMESCREEN_SITE = git://github.com/OpenVoiceOS/skill-ovos-homescreen
MYCROFT_SKILL_OVOS_HOMESCREEN_SITE_METHOD = git
MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME = skill-ovos-homescreen

define MYCROFT_SKILL_OVOS_HOMESCREEN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_HOMESCREEN_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
endef

$(eval $(generic-package))
