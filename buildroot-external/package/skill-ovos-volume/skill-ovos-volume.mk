################################################################################
#
# skill-ovos-volume
#
################################################################################

SKILL_OVOS_VOLUME_VERSION = 0feb9cfa55593ee011fdaf1141c6e5db864da104
SKILL_OVOS_VOLUME_SITE = $(call github,OpenVoiceOS,skill-ovos-volume,$(SKILL_OVOS_VOLUME_VERSION))
SKILL_OVOS_VOLUME_SETUP_TYPE = setuptools
SKILL_OVOS_VOLUME_LICENSE_FILES = LICENSE
SKILL_OVOS_VOLUME_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
