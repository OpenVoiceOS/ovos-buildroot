################################################################################
#
# mycroft-skill-joke
#
################################################################################

MYCROFT_SKILL_JOKE_VERSION = 3d361925654857989ccf0c7d9a34a113150aa180
MYCROFT_SKILL_JOKE_SITE = git://github.com/MycroftAI/skill-joke
MYCROFT_SKILL_JOKE_SITE_METHOD = git
MYCROFT_SKILL_JOKE_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_JOKE_DIRNAME = skill-joke.mycroftai

define MYCROFT_SKILL_JOKE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_JOKE_DIRLOCATION)/$(MYCROFT_SKILL_JOKE_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_JOKE_DIRLOCATION)/$(MYCROFT_SKILL_JOKE_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_JOKE_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_JOKE_DIRLOCATION)/$(MYCROFT_SKILL_JOKE_DIRNAME)
endef

$(eval $(generic-package))
