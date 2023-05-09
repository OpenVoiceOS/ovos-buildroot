################################################################################
#
# python-ovos-ocp-deezer-plugin
#
################################################################################

PYTHON_OVOS_OCP_DEEZER_PLUGIN_VERSION = 67d1ee8e6df4333c19e838c1ef248f871d47533f
PYTHON_OVOS_OCP_DEEZER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-deezer-plugin,$(PYTHON_OVOS_OCP_DEEZER_PLUGIN_VERSION))
PYTHON_OVOS_OCP_DEEZER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_DEEZER_PLUGIN_LICENSE_DEEZER = LICENSE
PYTHON_OVOS_OCP_DEEZER_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
