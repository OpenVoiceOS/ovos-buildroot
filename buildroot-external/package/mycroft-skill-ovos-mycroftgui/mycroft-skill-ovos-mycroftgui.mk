################################################################################
#
# mycroft-skill-ovos-mycroftgui
#
################################################################################

MYCROFT_SKILL_OVOS_MYCROFTGUI_VERSION = d98871d8cac30534f08a3ea846f26a413d8a23be
MYCROFT_SKILL_OVOS_MYCROFTGUI_SITE = git://github.com/OpenVoiceOS/skill-ovos-mycroftgui
MYCROFT_SKILL_OVOS_MYCROFTGUI_SITE_METHOD = git
MYCROFT_SKILL_OVOS_MYCROFTGUI_DIRLOCATION = opt/mycroft/skills
MYCROFT_SKILL_OVOS_MYCROFTGUI_DIRNAME = skill-ovos-mycroftgui

define MYCROFT_SKILL_OVOS_MYCROFTGUI_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_MYCROFTGUI_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_MYCROFTGUI_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_MYCROFTGUI_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_MYCROFTGUI_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_MYCROFTGUI_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_MYCROFTGUI_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_MYCROFTGUI_DIRNAME)
endef

$(eval $(generic-package))
