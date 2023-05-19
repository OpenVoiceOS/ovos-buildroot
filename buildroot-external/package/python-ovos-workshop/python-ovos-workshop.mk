################################################################################
#
# python-ovos-workshop
#
################################################################################

PYTHON_OVOS_WORKSHOP_VERSION = 13cab11cb79146dd1b4666a44eaa62c3be0224c4
PYTHON_OVOS_WORKSHOP_SITE = $(call github,OpenVoiceOS,OVOS-workshop,$(PYTHON_OVOS_WORKSHOP_VERSION))
PYTHON_OVOS_WORKSHOP_SETUP_TYPE = setuptools
PYTHON_OVOS_WORKSHOP_LICENSE_FILES = LICENSE
PYTHON_OVOS_WORKSHOP_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
