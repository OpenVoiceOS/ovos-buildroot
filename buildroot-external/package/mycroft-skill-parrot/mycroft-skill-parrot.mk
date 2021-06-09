################################################################################
#
# mycroft-skill-parrot
#
################################################################################

MYCROFT_SKILL_PARROT_VERSION = abef6ff959b622a32dfe6a2bcf8e47fe451a53e6
MYCROFT_SKILL_PARROT_SITE = git://github.com/JarbasSkills/skill-parrot
MYCROFT_SKILL_PARROT_SITE_METHOD = git
MYCROFT_SKILL_PARROT_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_PARROT_DIRNAME = skill-parrot.jarbasskills

define MYCROFT_SKILL_PARROT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_PARROT_DIRLOCATION)/$(MYCROFT_SKILL_PARROT_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_PARROT_DIRLOCATION)/$(MYCROFT_SKILL_PARROT_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_PARROT_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_PARROT_DIRLOCATION)/$(MYCROFT_SKILL_PARROT_DIRNAME)
endef

$(eval $(generic-package))
