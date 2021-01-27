################################################################################
#
# mycroft-skill-ovos-homescreen
#
################################################################################

MYCROFT_SKILL_OVOS_HOMESCREEN_VERSION = 6affba69d1bc42d93b29ad89a181c9402b226c35
MYCROFT_SKILL_OVOS_HOMESCREEN_SITE = git://github.com/OpenVoiceOS/skill-ovos-homescreen
MYCROFT_SKILL_OVOS_HOMESCREEN_SITE_METHOD = git
MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION = opt/mycroft/skills
MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME = skill-ovos-homescreen

define MYCROFT_SKILL_OVOS_HOMESCREEN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_HOMESCREEN_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
endef

$(eval $(generic-package))
