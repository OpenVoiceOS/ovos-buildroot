################################################################################
#
# mycroft-skill-installer
#
################################################################################

MYCROFT_SKILL_INSTALLER_VERSION = cea3b98808aee400ece730dbdcd8957368d50983
MYCROFT_SKILL_INSTALLER_SITE = git://github.com/MycroftAI/skill-installer
MYCROFT_SKILL_INSTALLER_SITE_METHOD = git
MYCROFT_SKILL_INSTALLER_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_INSTALLER_DIRNAME = skill-installer.mycroftai

define MYCROFT_SKILL_INSTALLER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_INSTALLER_DIRLOCATION)/$(MYCROFT_SKILL_INSTALLER_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_INSTALLER_DIRLOCATION)/$(MYCROFT_SKILL_INSTALLER_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_INSTALLER_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_INSTALLER_DIRLOCATION)/$(MYCROFT_SKILL_INSTALLER_DIRNAME)
endef

$(eval $(generic-package))
