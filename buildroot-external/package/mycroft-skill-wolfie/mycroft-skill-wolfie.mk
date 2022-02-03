################################################################################
#
# mycroft-skill-wolfie
#
################################################################################

MYCROFT_SKILL_WOLFIE_VERSION = 8736018d95668ebe6c070111cabb3f1741ddfd79
MYCROFT_SKILL_WOLFIE_SITE = https://github.com/NeonJarbas/skill-wolfie
MYCROFT_SKILL_WOLFIE_SITE_METHOD = git
MYCROFT_SKILL_WOLFIE_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_WOLFIE_DIRNAME = skill-wolfie.jarbasskills

define MYCROFT_SKILL_WOLFIE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_WOLFIE_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
endef

$(eval $(generic-package))
