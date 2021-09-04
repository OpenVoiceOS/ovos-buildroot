################################################################################
#
# mycroft-skill-ovos-common-play
#
################################################################################

MYCROFT_SKILL_OVOS_COMMON_PLAY_VERSION = fe1f8c35de51fabf1406947d22fabc2dc3d2ee4e
MYCROFT_SKILL_OVOS_COMMON_PLAY_SITE = git://github.com/OpenVoiceOS/skill-ovos-common-play
MYCROFT_SKILL_OVOS_COMMON_PLAY_SITE_METHOD = git
MYCROFT_SKILL_OVOS_COMMON_PLAY_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_COMMON_PLAY_DIRNAME = skill-ovos-common-play.openvoiceos

define MYCROFT_SKILL_OVOS_COMMON_PLAY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_COMMON_PLAY_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_COMMON_PLAY_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_COMMON_PLAY_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_COMMON_PLAY_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_COMMON_PLAY_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_COMMON_PLAY_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_COMMON_PLAY_DIRNAME)
endef

$(eval $(generic-package))
