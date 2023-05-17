################################################################################
#
# python-ovos-workshop
#
################################################################################

PYTHON_OVOS_WORKSHOP_VERSION = 7649847b245aeb52bfcc27087830eca8a4df902c
PYTHON_OVOS_WORKSHOP_SITE = $(call github,OpenVoiceOS,OVOS-workshop,$(PYTHON_OVOS_WORKSHOP_VERSION))
PYTHON_OVOS_WORKSHOP_SETUP_TYPE = setuptools
PYTHON_OVOS_WORKSHOP_LICENSE_FILES = LICENSE
PYTHON_OVOS_WORKSHOP_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
