################################################################################
#
# python-ovos-config
#
################################################################################

PYTHON_OVOS_CONFIG_VERSION = 7df52cac6cbe369de43b06abb64e46cc83a29b7e
PYTHON_OVOS_CONFIG_SITE = $(call github,OpenVoiceOS,ovos-config,$(PYTHON_OVOS_CONFIG_VERSION))
PYTHON_OVOS_CONFIG_SETUP_TYPE = setuptools
PYTHON_OVOS_CONFIG_LICENSE_FILES = LICENSE
PYTHON_OVOS_CONFIG_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
