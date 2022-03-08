################################################################################
#
# mycroft-skill-personal
#
################################################################################

MYCROFT_SKILL_PERSONAL_VERSION = e4f04baee00b3b137ed317e1801e41f6d885cc91
MYCROFT_SKILL_PERSONAL_SITE = https://github.com/OpenVoiceOS/skill-personal
MYCROFT_SKILL_PERSONAL_SITE_METHOD = git
MYCROFT_SKILL_PERSONAL_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_PERSONAL_DIRNAME = skill-personal.openvoiceos

define MYCROFT_SKILL_PERSONAL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_PERSONAL_DIRLOCATION)/$(MYCROFT_SKILL_PERSONAL_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_PERSONAL_DIRLOCATION)/$(MYCROFT_SKILL_PERSONAL_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_PERSONAL_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_PERSONAL_DIRLOCATION)/$(MYCROFT_SKILL_PERSONAL_DIRNAME)
endef

$(eval $(generic-package))
