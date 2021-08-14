################################################################################
#
# mycroft-skill-news
#
################################################################################

MYCROFT_SKILL_NEWS_VERSION = 0bf5acc034c879759550c8f176bb3813bd1055cd
MYCROFT_SKILL_NEWS_SITE = git://github.com/JarbasSkills/skill-news
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
