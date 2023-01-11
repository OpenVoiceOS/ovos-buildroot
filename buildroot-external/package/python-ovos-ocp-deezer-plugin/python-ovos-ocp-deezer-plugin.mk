################################################################################
#
# python-ovos-ocp-deezer-plugin
#
################################################################################

PYTHON_OVOS_OCP_DEEZER_PLUGIN_VERSION = 13f55123c2a7aa602eee086a42fed1122e956898
PYTHON_OVOS_OCP_DEEZER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-deezer-plugin,$(PYTHON_OVOS_OCP_DEEZER_PLUGIN_VERSION))
PYTHON_OVOS_OCP_DEEZER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_DEEZER_PLUGIN_LICENSE_DEEZER = LICENSE
PYTHON_OVOS_OCP_DEEZER_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
