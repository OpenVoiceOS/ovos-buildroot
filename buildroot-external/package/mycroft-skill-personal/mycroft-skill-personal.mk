################################################################################
#
# mycroft-skill-personal
#
################################################################################

MYCROFT_SKILL_PERSONAL_VERSION = ed99a6a26f14383bd1a42beb29f137f1a53c4954
MYCROFT_SKILL_PERSONAL_SITE = git://github.com/MycroftAI/skill-personal
MYCROFT_SKILL_PERSONAL_SITE_METHOD = git
MYCROFT_SKILL_PERSONAL_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_PERSONAL_DIRNAME = skill-personal.mycroftai

define MYCROFT_SKILL_PERSONAL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_PERSONAL_DIRLOCATION)/$(MYCROFT_SKILL_PERSONAL_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_PERSONAL_DIRLOCATION)/$(MYCROFT_SKILL_PERSONAL_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_PERSONAL_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_PERSONAL_DIRLOCATION)/$(MYCROFT_SKILL_PERSONAL_DIRNAME)
endef

$(eval $(generic-package))
