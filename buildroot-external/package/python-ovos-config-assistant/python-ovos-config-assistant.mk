################################################################################
#
# python-ovos-config-assistant
#
################################################################################

PYTHON_OVOS_CONFIG_ASSISTANT_VERSION = 37ff3940ee52e50175d0b6f69bd2b7c397d5d583
PYTHON_OVOS_CONFIG_ASSISTANT_SITE = $(call github,OpenVoiceOS,ovos-config-assistant,$(PYTHON_OVOS_CONFIG_ASSISTANT_VERSION))
PYTHON_OVOS_CONFIG_ASSISTANT_SETUP_TYPE = setuptools
PYTHON_OVOS_CONFIG_ASSISTANT_LICENSE_FILES = LICENSE

$(eval $(python-package))
