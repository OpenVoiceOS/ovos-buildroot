################################################################################
#
# mycroft-skill-unknown
#
################################################################################

MYCROFT_SKILL_UNKNOWN_VERSION = de219550beccaaccb9310b200943ed5a2b2dbaf2
MYCROFT_SKILL_UNKNOWN_SITE = git://github.com/MycroftAI/fallback-unknown
MYCROFT_SKILL_UNKNOWN_SITE_METHOD = git
MYCROFT_SKILL_UNKNOWN_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_UNKNOWN_DIRNAME = fallback-unknown.mycroftai

define MYCROFT_SKILL_UNKNOWN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_UNKNOWN_DIRLOCATION)/$(MYCROFT_SKILL_UNKNOWN_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_UNKNOWN_DIRLOCATION)/$(MYCROFT_SKILL_UNKNOWN_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_UNKNOWN_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_UNKNOWN_DIRLOCATION)/$(MYCROFT_SKILL_UNKNOWN_DIRNAME)
endef

$(eval $(generic-package))
