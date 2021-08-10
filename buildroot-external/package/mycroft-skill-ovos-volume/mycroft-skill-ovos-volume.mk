################################################################################
#
# mycroft-skill-ovos-volume
#
################################################################################

MYCROFT_SKILL_OVOS_VOLUME_VERSION = d32811361918fcdef7ae1f0d36ea0a284c54d55c
MYCROFT_SKILL_OVOS_VOLUME_SITE = git://github.com/OpenVoiceOS/skill-ovos-volume
MYCROFT_SKILL_OVOS_VOLUME_SITE_METHOD = git
MYCROFT_SKILL_OVOS_VOLUME_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_VOLUME_DIRNAME = skill-ovos-volume.openvoiceos

define MYCROFT_SKILL_OVOS_VOLUME_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_VOLUME_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_VOLUME_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_VOLUME_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_VOLUME_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_VOLUME_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_VOLUME_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_VOLUME_DIRNAME)
endef

$(eval $(generic-package))
