################################################################################
#
# mycroft-skill-speak
#
################################################################################

MYCROFT_SKILL_SPEAK_VERSION = 6fb04f592950562e700d314f2b34bcbf1754d964
MYCROFT_SKILL_SPEAK_SITE = git://github.com/MycroftAI/skill-speak
MYCROFT_SKILL_SPEAK_SITE_METHOD = git
MYCROFT_SKILL_SPEAK_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_SPEAK_DIRNAME = mycroft-speak.mycroftai

define MYCROFT_SKILL_SPEAK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_SPEAK_DIRLOCATION)/$(MYCROFT_SKILL_SPEAK_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_SPEAK_DIRLOCATION)/$(MYCROFT_SKILL_SPEAK_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_SPEAK_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_SPEAK_DIRLOCATION)/$(MYCROFT_SKILL_SPEAK_DIRNAME)
endef

$(eval $(generic-package))
