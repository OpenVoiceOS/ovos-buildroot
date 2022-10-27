################################################################################
#
# python-ovos-config-assistant
#
################################################################################

PYTHON_OVOS_CONFIG_ASSISTANT_VERSION = fd2ac813342fbb3440b9337a310e46ad8603b56b
PYTHON_OVOS_CONFIG_ASSISTANT_SITE = $(call github,OpenVoiceOS,ovos-config-assistant,$(PYTHON_OVOS_CONFIG_ASSISTANT_VERSION))
PYTHON_OVOS_CONFIG_ASSISTANT_SETUP_TYPE = setuptools
PYTHON_OVOS_CONFIG_ASSISTANT_LICENSE_FILES = LICENSE

$(eval $(python-package))
