################################################################################
#
# mycroft-skill-spelling
#
################################################################################

MYCROFT_SKILL_SPELLING_VERSION = 89c154850cf79f3b2544337e42874adc9e0c7520
MYCROFT_SKILL_SPELLING_SITE = git://github.com/MycroftAI/skill-spelling
MYCROFT_SKILL_SPELLING_SITE_METHOD = git
MYCROFT_SKILL_SPELLING_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_SPELLING_DIRNAME = skill-spelling.mycroftai

define MYCROFT_SKILL_SPELLING_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_SPELLING_DIRLOCATION)/$(MYCROFT_SKILL_SPELLING_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_SPELLING_DIRLOCATION)/$(MYCROFT_SKILL_SPELLING_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_SPELLING_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_SPELLING_DIRLOCATION)/$(MYCROFT_SKILL_SPELLING_DIRNAME)
endef

$(eval $(generic-package))
