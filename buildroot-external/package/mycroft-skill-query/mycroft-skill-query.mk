################################################################################
#
# mycroft-skill-query
#
################################################################################

MYCROFT_SKILL_QUERY_VERSION = 8789731b6f0ba387039596fa64817549f12c35f5
MYCROFT_SKILL_QUERY_SITE = git://github.com/MycroftAI/skill-query
MYCROFT_SKILL_QUERY_SITE_METHOD = git
MYCROFT_SKILL_QUERY_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_QUERY_DIRNAME = skill-query.mycroftai

define MYCROFT_SKILL_QUERY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_QUERY_DIRLOCATION)/$(MYCROFT_SKILL_QUERY_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_QUERY_DIRLOCATION)/$(MYCROFT_SKILL_QUERY_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_QUERY_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_QUERY_DIRLOCATION)/$(MYCROFT_SKILL_QUERY_DIRNAME)
endef

$(eval $(generic-package))
