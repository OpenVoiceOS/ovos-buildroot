################################################################################
#
# mycroft-skill-wikipedia-for-humans
#
################################################################################

MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_VERSION = d37d0fd927cede5f9c040de53ebf4571c628e6e4
MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_SITE = https://github.com/OpenVoiceOS/skill-wikipedia-for-humans
MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_SITE_METHOD = git
MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DIRNAME = skill-wikipedia-for-humans.openvoiceos

define MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DIRLOCATION)/$(MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DIRLOCATION)/$(MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DIRLOCATION)/$(MYCROFT_SKILL_WIKIPEDIA_FOR_HUMANS_DIRNAME)
endef

$(eval $(generic-package))
