################################################################################
#
# python-ovos-config
#
################################################################################

PYTHON_OVOS_CONFIG_VERSION = 1b93f1a8806877777dc91f1598b01c14cb7d092c
PYTHON_OVOS_CONFIG_SITE = $(call github,OpenVoiceOS,ovos-config,$(PYTHON_OVOS_CONFIG_VERSION))
PYTHON_OVOS_CONFIG_SETUP_TYPE = setuptools
PYTHON_OVOS_CONFIG_LICENSE_FILES = LICENSE
PYTHON_OVOS_CONFIG_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
