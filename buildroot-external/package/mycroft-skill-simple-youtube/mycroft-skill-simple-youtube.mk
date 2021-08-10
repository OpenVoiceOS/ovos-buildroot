################################################################################
#
# mycroft-skill-simple-youtube
#
################################################################################

MYCROFT_SKILL_SIMPLE_YOUTUBE_VERSION = 2076faceeb393ae80e570c0b50094807450d4ec3
MYCROFT_SKILL_SIMPLE_YOUTUBE_SITE = git://github.com/JarbasSkills/skill-simple-youtube
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
