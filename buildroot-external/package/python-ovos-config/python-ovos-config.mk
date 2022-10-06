################################################################################
#
# python-ovos-config
#
################################################################################

PYTHON_OVOS_CONFIG_VERSION = 3277b10d8ffad8296d144bccbd0ec2dda9a0a9d8
PYTHON_OVOS_CONFIG_SITE = $(call github,OpenVoiceOS,ovos-config,$(PYTHON_OVOS_CONFIG_VERSION))
PYTHON_OVOS_CONFIG_SETUP_TYPE = setuptools
PYTHON_OVOS_CONFIG_LICENSE_FILES = LICENSE
PYTHON_OVOS_CONFIG_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
