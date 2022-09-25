################################################################################
#
# python-ovos-workshop
#
################################################################################

PYTHON_OVOS_WORKSHOP_VERSION = 55d2cde93378819bcf9fdeaf168d8cfa0dca8f25
PYTHON_OVOS_WORKSHOP_SITE = $(call github,OpenVoiceOS,OVOS-workshop,$(PYTHON_OVOS_WORKSHOP_VERSION))
PYTHON_OVOS_WORKSHOP_SETUP_TYPE = setuptools
PYTHON_OVOS_WORKSHOP_LICENSE_FILES = LICENSE

$(eval $(python-package))
