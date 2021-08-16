################################################################################
#
# mycroft-skill-alarm
#
################################################################################

MYCROFT_SKILL_ALARM_VERSION = 25ecc0261abee644257a81f20f020bb92f462970
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
