################################################################################
#
# python-ovos-phal
#
################################################################################

PYTHON_OVOS_PHAL_VERSION = 0f0003cedb8b6c9ed0846a85f9c1bd0a55d73d44
PYTHON_OVOS_PHAL_SITE = $(call github,OpenVoiceOS,ovos_PHAL,$(PYTHON_OVOS_PHAL_VERSION))
PYTHON_OVOS_PHAL_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
