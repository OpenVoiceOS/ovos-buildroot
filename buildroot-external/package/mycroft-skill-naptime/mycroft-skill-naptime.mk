################################################################################
#
# mycroft-skill-naptime
#
################################################################################

MYCROFT_SKILL_NAPTIME_VERSION = e7cc937918cc09c1781fc3b09c0bf5685eafc137
MYCROFT_SKILL_NAPTIME_SITE = git://github.com/MycroftAI/skill-naptime
MYCROFT_SKILL_NAPTIME_SITE_METHOD = git
MYCROFT_SKILL_NAPTIME_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_NAPTIME_DIRNAME = mycroft-naptime.mycroftai

define MYCROFT_SKILL_NAPTIME_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_NAPTIME_DIRLOCATION)/$(MYCROFT_SKILL_NAPTIME_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_NAPTIME_DIRLOCATION)/$(MYCROFT_SKILL_NAPTIME_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_NAPTIME_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_NAPTIME_DIRLOCATION)/$(MYCROFT_SKILL_NAPTIME_DIRNAME)
endef

$(eval $(generic-package))
