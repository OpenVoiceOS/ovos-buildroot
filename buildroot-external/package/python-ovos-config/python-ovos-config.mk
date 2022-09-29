################################################################################
#
# python-ovos-config
#
################################################################################

PYTHON_OVOS_CONFIG_VERSION = fe9e3d2a7ad4a23f5b2cdc67705448b28a57db17
PYTHON_OVOS_CONFIG_SITE = $(call github,OpenVoiceOS,ovos-config,$(PYTHON_OVOS_CONFIG_VERSION))
PYTHON_OVOS_CONFIG_SETUP_TYPE = setuptools
PYTHON_OVOS_CONFIG_LICENSE_FILES = LICENSE
PYTHON_OVOS_CONFIG_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
