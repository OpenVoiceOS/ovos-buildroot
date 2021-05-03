################################################################################
#
# mycroft-skill-alarm
#
################################################################################

MYCROFT_SKILL_ALARM_VERSION = 7bce0ee39867b3e1cf81c33c81d7830afd34e1b3
MYCROFT_SKILL_ALARM_SITE = git://github.com/MycroftAI/skill-alarm
MYCROFT_SKILL_ALARM_SITE_METHOD = git
MYCROFT_SKILL_ALARM_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_ALARM_DIRNAME = mycroft-alarm.mycroftai

define MYCROFT_SKILL_ALARM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_ALARM_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_ALARM_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_ALARM_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_ALARM_DIRLOCATION)/$(MYCROFT_SKILL_ALARM_DIRNAME)
endef

$(eval $(generic-package))
