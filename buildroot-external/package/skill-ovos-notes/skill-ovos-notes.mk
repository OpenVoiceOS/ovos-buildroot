################################################################################
#
# skill-ovos-notes
#
################################################################################

SKILL_OVOS_NOTES_VERSION = 36cbc0b2e1daabf08df3c0d170b54f7a5b10ad1b
SKILL_OVOS_NOTES_SITE = $(call github,OpenVoiceOS,skill-ovos-notes,$(SKILL_OVOS_NOTES_VERSION))
SKILL_OVOS_NOTES_SETUP_TYPE = setuptools
SKILL_OVOS_NOTES_LICENSE_FILES = LICENSE

$(eval $(python-package))
