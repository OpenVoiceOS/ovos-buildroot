################################################################################
#
# mycroft-skill-singing
#
################################################################################

MYCROFT_SKILL_SINGING_VERSION = 3cfd5007ac2b0c728bb5557ca68a99eea20e818f
MYCROFT_SKILL_SINGING_SITE = git://github.com/MycroftAI/skill-singing
MYCROFT_SKILL_SINGING_SITE_METHOD = git
MYCROFT_SKILL_SINGING_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_SINGING_DIRNAME = skill-singing.mycroftai

define MYCROFT_SKILL_SINGING_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_SINGING_DIRLOCATION)/$(MYCROFT_SKILL_SINGING_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_SINGING_DIRLOCATION)/$(MYCROFT_SKILL_SINGING_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_SINGING_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_SINGING_DIRLOCATION)/$(MYCROFT_SKILL_SINGING_DIRNAME)
endef

$(eval $(generic-package))
