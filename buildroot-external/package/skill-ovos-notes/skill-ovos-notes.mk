################################################################################
#
# skill-ovos-notes
#
################################################################################

SKILL_OVOS_NOTES_VERSION = adcfc50268846852f16cb9205a1dae26055151c4
SKILL_OVOS_NOTES_SITE = $(call github,OpenVoiceOS,skill-ovos-notes,$(SKILL_OVOS_NOTES_VERSION))
SKILL_OVOS_NOTES_SETUP_TYPE = setuptools
SKILL_OVOS_NOTES_LICENSE_FILES = LICENSE

$(eval $(python-package))
