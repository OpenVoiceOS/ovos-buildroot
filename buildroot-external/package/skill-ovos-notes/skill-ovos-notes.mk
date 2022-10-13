################################################################################
#
# skill-ovos-notes
#
################################################################################

SKILL_OVOS_NOTES_VERSION = d4522f4bb544fe98324133781d6af82eaa25a520
SKILL_OVOS_NOTES_SITE = $(call github,OpenVoiceOS,skill-ovos-notes,$(SKILL_OVOS_NOTES_VERSION))
SKILL_OVOS_NOTES_SETUP_TYPE = setuptools
SKILL_OVOS_NOTES_LICENSE_FILES = LICENSE

$(eval $(python-package))
