################################################################################
#
# mycroft-skill-timer
#
################################################################################

MYCROFT_SKILL_TIMER_VERSION = ccca4656760f7ae9bdfa4565eedca511d0c4bacc
MYCROFT_SKILL_TIMER_SITE = https://github.com/MycroftAI/mycroft-timer
MYCROFT_SKILL_TIMER_SITE_METHOD = git
MYCROFT_SKILL_TIMER_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_TIMER_DIRNAME = mycroft-timer.mycroftai

define MYCROFT_SKILL_TIMER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_TIMER_DIRLOCATION)/$(MYCROFT_SKILL_TIMER_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_TIMER_DIRLOCATION)/$(MYCROFT_SKILL_TIMER_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_TIMER_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_TIMER_DIRLOCATION)/$(MYCROFT_SKILL_TIMER_DIRNAME)
endef

$(eval $(generic-package))
