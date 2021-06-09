################################################################################
#
# mycroft-skill-better-stop
#
################################################################################

MYCROFT_SKILL_BETTER_STOP_VERSION = b3e9983f341a94740db7d7cbbd9533230f032969
MYCROFT_SKILL_BETTER_STOP_SITE = git://github.com/JarbasSkills/skill-better-stop
MYCROFT_SKILL_BETTER_STOP_SITE_METHOD = git
MYCROFT_SKILL_BETTER_STOP_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_BETTER_STOP_DIRNAME = skill-better-stop.jarbasskills

define MYCROFT_SKILL_BETTER_STOP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_BETTER_STOP_DIRLOCATION)/$(MYCROFT_SKILL_BETTER_STOP_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_BETTER_STOP_DIRLOCATION)/$(MYCROFT_SKILL_BETTER_STOP_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_BETTER_STOP_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_BETTER_STOP_DIRLOCATION)/$(MYCROFT_SKILL_BETTER_STOP_DIRNAME)
endef

$(eval $(generic-package))
