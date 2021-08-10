################################################################################
#
# mycroft-skill-alarm
#
################################################################################

MYCROFT_SKILL_ALARM_VERSION = b7c728de3d4fa691719a3d37e0197b0f7c031f96
MYCROFT_SKILL_ALARM_SITE = git://github.com/MycroftAI/skill-alarm
MYCROFT_SKILL_ALARM_SITE_METHOD = git
MYCROFT_SKILL_ALARM_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_ALARM_DIRNAME = skill-alarm.mycroftai

define MYCROFT_SKILL_ALARM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_ALARM_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_ALARM_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_ALARM_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_ALARM_DIRNAME)
endef

$(eval $(generic-package))
