################################################################################
#
# skill-ovos-volume
#
################################################################################

SKILL_OVOS_VOLUME_VERSION = 9f6aa4579959536aa41335fc606bd12a167f67cb
SKILL_OVOS_VOLUME_SITE = $(call github,OpenVoiceOS,skill-ovos-volume,$(SKILL_OVOS_VOLUME_VERSION))
SKILL_OVOS_VOLUME_SETUP_TYPE = setuptools
SKILL_OVOS_VOLUME_LICENSE_FILES = LICENSE
SKILL_OVOS_VOLUME_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
