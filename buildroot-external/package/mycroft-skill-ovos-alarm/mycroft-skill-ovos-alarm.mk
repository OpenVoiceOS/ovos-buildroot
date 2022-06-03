################################################################################
#
# mycroft-skill-ovos-alarm
#
################################################################################

MYCROFT_SKILL_OVOS_ALARM_VERSION = 
MYCROFT_SKILL_OVOS_ALARM_SITE = https://github.com/OpenVoiceOS/skill-ovos-alarm
MYCROFT_SKILL_OVOS_ALARM_SITE_METHOD = git
MYCROFT_SKILL_OVOS_ALARM_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_ALARM_DIRNAME = skill-ovos-alarm.openvoiceos

define MYCROFT_SKILL_OVOS_ALARM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_ALARM_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_ALARM_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_ALARM_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_ALARM_DIRNAME)
endef

$(eval $(generic-package))
