################################################################################
#
# mycroft-skill-ddg
#
################################################################################

MYCROFT_SKILL_DDG_VERSION = 72dc55998fd7d2817259f2d757fd0f7e5b9b14e1
MYCROFT_SKILL_DDG_SITE = https://github.com/OpenVoiceOS/skill-ddg
MYCROFT_SKILL_DDG_SITE_METHOD = git
MYCROFT_SKILL_DDG_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_DDG_DIRNAME = skill-ddg.openvoiceos

define MYCROFT_SKILL_DDG_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_DDG_DIRLOCATION)/$(MYCROFT_SKILL_DDG_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_DDG_DIRLOCATION)/$(MYCROFT_SKILL_DDG_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_DDG_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_DDG_DIRLOCATION)/$(MYCROFT_SKILL_DDG_DIRNAME)
endef

$(eval $(generic-package))
