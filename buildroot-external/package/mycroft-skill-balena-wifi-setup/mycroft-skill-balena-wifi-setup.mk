################################################################################
#
# mycroft-skill-balena-wifi-setup
#
################################################################################

MYCROFT_SKILL_BALENA_WIFI_SETUP_VERSION = 22fca33100c6f197f6f11c38795de723503eb44b
MYCROFT_SKILL_BALENA_WIFI_SETUP_SITE = https://github.com/OpenVoiceOS/skill-balena-wifi-setup
MYCROFT_SKILL_BALENA_WIFI_SETUP_SITE_METHOD = git
MYCROFT_SKILL_BALENA_WIFI_SETUP_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_BALENA_WIFI_SETUP_DIRNAME = skill-balena-wifi-setup.openvoiceos

define MYCROFT_SKILL_BALENA_WIFI_SETUP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_BALENA_WIFI_SETUP_DIRLOCATION)/$(MYCROFT_SKILL_BALENA_WIFI_SETUP_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_BALENA_WIFI_SETUP_DIRLOCATION)/$(MYCROFT_SKILL_BALENA_WIFI_SETUP_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_BALENA_WIFI_SETUP_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_BALENA_WIFI_SETUP_DIRLOCATION)/$(MYCROFT_SKILL_BALENA_WIFI_SETUP_DIRNAME)
endef

$(eval $(generic-package))
