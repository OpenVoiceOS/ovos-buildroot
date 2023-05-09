################################################################################
#
# python-ovos-ocp-m3u-plugin
#
################################################################################

PYTHON_OVOS_OCP_M3U_PLUGIN_VERSION = d2571ac1c2870501f0940dc3dcdb35b402300e9e
PYTHON_OVOS_OCP_M3U_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-m3u-plugin,$(PYTHON_OVOS_OCP_M3U_PLUGIN_VERSION))
PYTHON_OVOS_OCP_M3U_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_M3U_PLUGIN_LICENSE_M3U = LICENSE
PYTHON_OVOS_OCP_M3U_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
