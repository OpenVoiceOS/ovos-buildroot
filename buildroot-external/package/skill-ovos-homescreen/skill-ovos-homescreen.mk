################################################################################
#
# skill-ovos-homescreen
#
################################################################################

SKILL_OVOS_HOMESCREEN_VERSION = 9f27f970745f5f87e1778e50f82f039edf1f225d
SKILL_OVOS_HOMESCREEN_SITE = $(call github,OpenVoiceOS,skill-ovos-homescreen,$(SKILL_OVOS_HOMESCREEN_VERSION))
SKILL_OVOS_HOMESCREEN_SETUP_TYPE = setuptools
SKILL_OVOS_HOMESCREEN_LICENSE_FILES = LICENSE

$(eval $(python-package))
