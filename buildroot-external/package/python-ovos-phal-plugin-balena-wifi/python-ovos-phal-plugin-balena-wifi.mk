################################################################################
#
# python-ovos-phal-plugin-balena-wifi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION = 099b47530ba5413170ba30e9fea397c22a8edea0
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-balena-wifi,$(PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
