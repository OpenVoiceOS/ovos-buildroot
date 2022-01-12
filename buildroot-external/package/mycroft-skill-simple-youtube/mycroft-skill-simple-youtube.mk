################################################################################
#
# mycroft-skill-simple-youtube
#
################################################################################

MYCROFT_SKILL_SIMPLE_YOUTUBE_VERSION = 9c01487e8094a3f575e9d9ee212c6ee55335d7dc
MYCROFT_SKILL_SIMPLE_YOUTUBE_SITE = https://github.com/JarbasSkills/skill-simple-youtube
MYCROFT_SKILL_SIMPLE_YOUTUBE_SITE_METHOD = git
MYCROFT_SKILL_SIMPLE_YOUTUBE_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_SIMPLE_YOUTUBE_DIRNAME = skill-simple-youtube.jarbasskills

define MYCROFT_SKILL_SIMPLE_YOUTUBE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_SIMPLE_YOUTUBE_DIRLOCATION)/$(MYCROFT_SKILL_SIMPLE_YOUTUBE_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_SIMPLE_YOUTUBE_DIRLOCATION)/$(MYCROFT_SKILL_SIMPLE_YOUTUBE_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_SIMPLE_YOUTUBE_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_SIMPLE_YOUTUBE_DIRLOCATION)/$(MYCROFT_SKILL_SIMPLE_YOUTUBE_DIRNAME)
endef

$(eval $(generic-package))
