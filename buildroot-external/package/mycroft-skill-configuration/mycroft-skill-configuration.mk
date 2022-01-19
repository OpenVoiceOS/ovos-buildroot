################################################################################
#
# mycroft-skill-configuration
#
################################################################################

MYCROFT_SKILL_CONFIGURATION_VERSION = 9231778e959c65a4f8156923fb26d11483d72ea0
MYCROFT_SKILL_CONFIGURATION_SITE = https://github.com/MycroftAI/skill-configuration
MYCROFT_SKILL_CONFIGURATION_SITE_METHOD = git
MYCROFT_SKILL_CONFIGURATION_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_CONFIGURATION_DIRNAME = skill-configuration.mycroftai

define MYCROFT_SKILL_CONFIGURATION_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_CONFIGURATION_DIRLOCATION)/$(MYCROFT_SKILL_CONFIGURATION_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_CONFIGURATION_DIRLOCATION)/$(MYCROFT_SKILL_CONFIGURATION_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_CONFIGURATION_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_CONFIGURATION_DIRLOCATION)/$(MYCROFT_SKILL_CONFIGURATION_DIRNAME)
endef

$(eval $(generic-package))
