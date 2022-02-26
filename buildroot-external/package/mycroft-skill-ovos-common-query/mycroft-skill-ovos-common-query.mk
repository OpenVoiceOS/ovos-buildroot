################################################################################
#
# mycroft-skill-query
#
################################################################################

MYCROFT_SKILL_OVOS_COMMON_QUERY_VERSION = e7fe7fda707707082b0c82d5fafb7ac8f2f98913
MYCROFT_SKILL_OVOS_COMMON_QUERY_SITE = https://github.com/OpenVoiceOS/skill-ovos-common-query
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
