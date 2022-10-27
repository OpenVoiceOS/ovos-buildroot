################################################################################
#
# skill-ovos-settings
#
################################################################################

SKILL_OVOS_SETTINGS_VERSION = ea3bbcd98049f8e725c1363ebf55d3c79ee1ea2c
SKILL_OVOS_SETTINGS_SITE = $(call github,OpenVoiceOS,skill-ovos-settings,$(SKILL_OVOS_SETTINGS_VERSION))
SKILL_OVOS_SETTINGS_SETUP_TYPE = setuptools
SKILL_OVOS_SETTINGS_LICENSE_FILES = LICENSE

$(eval $(python-package))
