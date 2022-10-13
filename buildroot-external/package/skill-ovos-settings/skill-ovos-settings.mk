################################################################################
#
# skill-ovos-settings
#
################################################################################

SKILL_OVOS_SETTINGS_VERSION = ffcdd6124f553aba9c540afe6e7fef4f3b2b0d57
SKILL_OVOS_SETTINGS_SITE = $(call github,OpenVoiceOS,skill-ovos-settings,$(SKILL_OVOS_SETTINGS_VERSION))
SKILL_OVOS_SETTINGS_SETUP_TYPE = setuptools
SKILL_OVOS_SETTINGS_LICENSE_FILES = LICENSE

$(eval $(python-package))
