################################################################################
#
# skill-ovos-settings
#
################################################################################

SKILL_OVOS_SETTINGS_VERSION = aa25d3424d49efe193233eb1b1f3f83b813f7f8b
SKILL_OVOS_SETTINGS_SITE = $(call github,OpenVoiceOS,skill-ovos-settings,$(SKILL_OVOS_SETTINGS_VERSION))
SKILL_OVOS_SETTINGS_SETUP_TYPE = setuptools
SKILL_OVOS_SETTINGS_LICENSE_FILES = LICENSE

$(eval $(python-package))
