################################################################################
#
# mycroft-skill-wolfie
#
################################################################################

MYCROFT_SKILL_WOLFIE_VERSION = c5ff51a0c5390cbf579293f74e30028061453344
MYCROFT_SKILL_WOLFIE_SITE = https://github.com/OpenVoiceOS/skill-wolfie
MYCROFT_SKILL_WOLFIE_SITE_METHOD = git
MYCROFT_SKILL_WOLFIE_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_WOLFIE_DIRNAME = skill-wolfie.openvoiceos

define MYCROFT_SKILL_WOLFIE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_WOLFIE_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
endef

$(eval $(generic-package))
