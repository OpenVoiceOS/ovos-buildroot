################################################################################
#
# python-ovos-config
#
################################################################################

PYTHON_OVOS_CONFIG_VERSION = 53597873e570cd26c9cd9c52b99404e9c3383fd3
PYTHON_OVOS_CONFIG_SITE = $(call github,OpenVoiceOS,ovos-config,$(PYTHON_OVOS_CONFIG_VERSION))
PYTHON_OVOS_CONFIG_SETUP_TYPE = setuptools
PYTHON_OVOS_CONFIG_LICENSE_FILES = LICENSE
PYTHON_OVOS_CONFIG_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
