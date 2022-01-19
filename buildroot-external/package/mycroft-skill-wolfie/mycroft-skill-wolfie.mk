################################################################################
#
# mycroft-skill-wolfie
#
################################################################################

MYCROFT_SKILL_WOLFIE_VERSION = f81ae02ac0830662ba3a9425a1016de647db4c8a
MYCROFT_SKILL_WOLFIE_SITE = https://github.com/JarbasSkills/skill-wolfie
MYCROFT_SKILL_WOLFIE_SITE_METHOD = git
MYCROFT_SKILL_WOLFIE_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_WOLFIE_DIRNAME = skill-wolfie.jarbasskills

define MYCROFT_SKILL_WOLFIE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_WOLFIE_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_WOLFIE_DIRLOCATION)/$(MYCROFT_SKILL_WOLFIE_DIRNAME)
endef

$(eval $(generic-package))
