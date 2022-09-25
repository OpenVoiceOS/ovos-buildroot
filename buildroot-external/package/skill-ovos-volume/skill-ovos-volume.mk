################################################################################
#
# skill-ovos-volume
#
################################################################################

SKILL_OVOS_VOLUME_VERSION = 9627e031e883f30bd7d64052e7d5d17b2d239ad8
SKILL_OVOS_VOLUME_SITE = $(call github,OpenVoiceOS,skill-ovos-volume,$(SKILL_OVOS_VOLUME_VERSION))
SKILL_OVOS_VOLUME_SETUP_TYPE = setuptools
SKILL_OVOS_VOLUME_LICENSE_FILES = LICENSE

$(eval $(python-package))
