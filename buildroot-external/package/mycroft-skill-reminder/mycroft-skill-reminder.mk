################################################################################
#
# mycroft-skill-reminder
#
################################################################################

MYCROFT_SKILL_REMINDER_VERSION = a2e615c09bfe5ebf6471f10167e2f9dff858c872
MYCROFT_SKILL_REMINDER_SITE = git://github.com/MycroftAI/skill-reminder
MYCROFT_SKILL_REMINDER_SITE_METHOD = git
MYCROFT_SKILL_REMINDER_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_REMINDER_DIRNAME = skill-reminder.mycroftai

define MYCROFT_SKILL_REMINDER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_REMINDER_DIRLOCATION)/$(MYCROFT_SKILL_REMINDER_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_REMINDER_DIRLOCATION)/$(MYCROFT_SKILL_REMINDER_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_REMINDER_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_REMINDER_DIRLOCATION)/$(MYCROFT_SKILL_REMINDER_DIRNAME)
endef

$(eval $(generic-package))
