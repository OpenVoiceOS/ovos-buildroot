################################################################################
#
# mycroft-skill-ovos-stop
#
################################################################################

MYCROFT_SKILL_OVOS_STOP_VERSION = 008caa082d25bd9d4c7535b41ccf627c27df9c08
MYCROFT_SKILL_OVOS_STOP_SITE = https://github.com/OpenVoiceOS/skill-ovos-stop
MYCROFT_SKILL_OVOS_STOP_SITE_METHOD = git
MYCROFT_SKILL_OVOS_STOP_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_STOP_DIRNAME = skill-ovos-stop.openvoiceos

define MYCROFT_SKILL_OVOS_STOP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_STOP_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_STOP_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_STOP_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_STOP_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_STOP_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_STOP_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_STOP_DIRNAME)
endef

$(eval $(generic-package))
