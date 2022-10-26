################################################################################
#
# skill-ovos-setup
#
################################################################################

SKILL_OVOS_SETUP_VERSION = 9ed3ba2eedbbf7616b59d5832a96d23fcee3ff73
SKILL_OVOS_SETUP_SITE = $(call github,OpenVoiceOS,skill-ovos-setup,$(SKILL_OVOS_SETUP_VERSION))
SKILL_OVOS_SETUP_SETUP_TYPE = setuptools
SKILL_OVOS_SETUP_LICENSE_FILES = LICENSE
SKILL_OVOS_SETUP_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
