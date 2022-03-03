################################################################################
#
# python-ovos-config-assistant
#
################################################################################

PYTHON_OVOS_CONFIG_ASSISTANT_VERSION = ad0881569f6d0531a68bfd6687690103d927d14f
PYTHON_OVOS_CONFIG_ASSISTANT_SITE = $(call github,OpenVoiceOS,ovos-config-assistant,$(PYTHON_OVOS_CONFIG_ASSISTANT_VERSION))
PYTHON_OVOS_CONFIG_ASSISTANT_SETUP_TYPE = setuptools
PYTHON_OVOS_CONFIG_ASSISTANT_LICENSE_FILES = LICENSE

$(eval $(python-package))
