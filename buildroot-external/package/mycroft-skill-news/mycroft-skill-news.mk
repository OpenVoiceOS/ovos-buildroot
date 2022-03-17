################################################################################
#
# mycroft-skill-news
#
################################################################################

MYCROFT_SKILL_NEWS_VERSION = 7959296f189fd5e06807b9b7fc8fb9d23b22635f
MYCROFT_SKILL_NEWS_SITE = https://github.com/JarbasSkills/skill-news
MYCROFT_SKILL_NEWS_SITE_METHOD = git
MYCROFT_SKILL_NEWS_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_NEWS_DIRNAME = skill-news.jarbasskills

define MYCROFT_SKILL_NEWS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_NEWS_DIRLOCATION)/$(MYCROFT_SKILL_NEWS_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_NEWS_DIRLOCATION)/$(MYCROFT_SKILL_NEWS_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_NEWS_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_NEWS_DIRLOCATION)/$(MYCROFT_SKILL_NEWS_DIRNAME)
endef

$(eval $(generic-package))
