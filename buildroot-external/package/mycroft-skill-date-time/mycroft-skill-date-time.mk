################################################################################
#
# mycroft-skill-date-time
#
################################################################################

MYCROFT_SKILL_DATE_TIME_VERSION = d64f0329a6b6307438b5d59727205753db41ec61
MYCROFT_SKILL_DATE_TIME_SITE = git://github.com/MycroftAI/skill-date-time
MYCROFT_SKILL_DATE_TIME_SITE_METHOD = git
MYCROFT_SKILL_DATE_TIME_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_DATE_TIME_DIRNAME = skill-date-time.mycroftai

define MYCROFT_SKILL_DATE_TIME_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_DATE_TIME_DIRLOCATION)/$(MYCROFT_SKILL_DATE_TIME_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_DATE_TIME_DIRLOCATION)/$(MYCROFT_SKILL_DATE_TIME_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_DATE_TIME_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_DATE_TIME_DIRLOCATION)/$(MYCROFT_SKILL_DATE_TIME_DIRNAME)
endef

$(eval $(generic-package))
