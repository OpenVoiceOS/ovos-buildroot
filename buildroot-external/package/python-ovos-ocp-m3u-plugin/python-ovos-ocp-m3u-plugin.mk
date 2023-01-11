################################################################################
#
# python-ovos-ocp-m3u-plugin
#
################################################################################

PYTHON_OVOS_OCP_M3U_PLUGIN_VERSION = aec50ace75e488ea0316ef9a6b024fe7430267fb
PYTHON_OVOS_OCP_M3U_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-m3u-plugin,$(PYTHON_OVOS_OCP_M3U_PLUGIN_VERSION))
PYTHON_OVOS_OCP_M3U_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_M3U_PLUGIN_LICENSE_M3U = LICENSE
PYTHON_OVOS_OCP_M3U_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
