################################################################################
#
# mycroft-skill-notes
#
################################################################################

MYCROFT_SKILL_OVOS_NOTES_VERSION = d4634fa3258501d5cb31d150c8ea8b0e2e636eda
MYCROFT_SKILL_OVOS_NOTES_SITE = https://github.com/OpenVoiceOS/skill-ovos-notes
MYCROFT_SKILL_OVOS_NOTES_SITE_METHOD = git
MYCROFT_SKILL_OVOS_NOTES_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_NOTES_DIRNAME = skill-ovos-timer.openvoiceos

define MYCROFT_SKILL_OVOS_NOTES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_NOTES_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_NOTES_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_NOTES_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_NOTES_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_NOTES_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_NOTES_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_NOTES_DIRNAME)
endef

$(eval $(generic-package))
