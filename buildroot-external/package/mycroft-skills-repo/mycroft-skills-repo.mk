################################################################################
#
# mycroft-skills-repo
#
################################################################################

MYCROFT_SKILLS_REPO_VERSION = 20.08
MYCROFT_SKILLS_REPO_SITE = git://github.com/MycroftAI/mycroft-skills
MYCROFT_SKILLS_REPO_SITE_METHOD = git
#MYCROFT_SKILLS_REPO_GIT_SUBMODULES = yes
MYCROFT_SKILLS_REPO_DIRLOCATION = opt/mycroft
MYCROFT_SKILLS_REPO_DIRNAME = .skills-repo

define MYCROFT_SKILLS_REPO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILLS_REPO_DIRLOCATION)/$(MYCROFT_SKILLS_REPO_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILLS_REPO_DIRLOCATION)/$(MYCROFT_SKILLS_REPO_DIRNAME)
	cp -dpfr $(MYCROFT_SKILLS_REPO_DL_DIR)/git/* \
		$(TARGET_DIR)/$(MYCROFT_SKILLS_REPO_DIRLOCATION)/$(MYCROFT_SKILLS_REPO_DIRNAME)
endef

$(eval $(generic-package))
