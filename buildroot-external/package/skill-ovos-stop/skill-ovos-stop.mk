################################################################################
#
# skill-ovos-stop
#
################################################################################

SKILL_OVOS_STOP_VERSION = f0fa6b19f84503288fe9a927f37c0a135528eab1
SKILL_OVOS_STOP_SITE = $(call github,OpenVoiceOS,skill-ovos-stop,$(SKILL_OVOS_STOP_VERSION))
SKILL_OVOS_STOP_SETUP_TYPE = setuptools
SKILL_OVOS_STOP_LICENSE_FILES = LICENSE
SKILL_OVOS_STOP_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
