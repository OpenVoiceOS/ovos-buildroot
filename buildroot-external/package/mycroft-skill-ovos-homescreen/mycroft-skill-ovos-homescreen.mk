################################################################################
#
# mycroft-skill-ovos-homescreen
#
################################################################################

MYCROFT_SKILL_OVOS_HOMESCREEN_VERSION = e22cfb44a09730b6c632d21901b0cc279f60715f
MYCROFT_SKILL_OVOS_HOMESCREEN_SITE = git://github.com/OpenVoiceOS/skill-ovos-homescreen
MYCROFT_SKILL_OVOS_HOMESCREEN_SITE_METHOD = git
MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME = skill-ovos-homescreen.openvoiceos

define MYCROFT_SKILL_OVOS_HOMESCREEN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_HOMESCREEN_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_HOMESCREEN_DIRNAME)
endef

$(eval $(generic-package))
