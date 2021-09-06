################################################################################
#
# mycroft-skill-query
#
################################################################################

MYCROFT_SKILL_OVOS_COMMON_QUERY_VERSION = 2189e60b204b9f8b96d7a64429627736b714f399
MYCROFT_SKILL_OVOS_COMMON_QUERY_SITE = git://github.com/OpenVoiceOS/skill-ovos-common-query
MYCROFT_SKILL_OVOS_COMMON_QUERY_SITE_METHOD = git
MYCROFT_SKILL_OVOS_COMMON_QUERY_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OVOS_COMMON_QUERY_DIRNAME = skill-ovos-common-query.openvoiceos

define MYCROFT_SKILL_OVOS_COMMON_QUERY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_COMMON_QUERY_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_COMMON_QUERY_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_COMMON_QUERY_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_COMMON_QUERY_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OVOS_COMMON_QUERY_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OVOS_COMMON_QUERY_DIRLOCATION)/$(MYCROFT_SKILL_OVOS_COMMON_QUERY_DIRNAME)
endef

$(eval $(generic-package))
