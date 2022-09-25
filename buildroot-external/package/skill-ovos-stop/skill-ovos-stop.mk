################################################################################
#
# skill-ovos-stop
#
################################################################################

SKILL_OVOS_STOP_VERSION = 008caa082d25bd9d4c7535b41ccf627c27df9c08
SKILL_OVOS_STOP_SITE = $(call github,OpenVoiceOS,skill-ovos-stop,$(SKILL_OVOS_STOP_VERSION))
SKILL_OVOS_STOP_SETUP_TYPE = setuptools
SKILL_OVOS_STOP_LICENSE_FILES = LICENSE

$(eval $(python-package))
