################################################################################
#
# mycroft-skill-timer
#
################################################################################

MYCROFT_SKILL_OVOS_TIMER_VERSION = 72a3b0a88481d06f604c609f14a73cac4ab1b0e0
MYCROFT_SKILL_OVOS_TIMER_SITE = https://github.com/OpenVoiceOS/skill-ovos-timer
MYCROFT_SKILL_OVOS_TIMER_SITE_METHOD = git
MYCROFT_SKILL_OVOS_TIMER_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_TIMER_DIRNAME = skill-ovos-timer.openvoiceos

define MYCROFT_SKILL_OVOS_TIMER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_TIMER_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_TIMER_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_TIMER_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_TIMER_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_TIMER_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_TIMER_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_TIMER_DIRNAME)
endef

$(eval $(generic-package))
