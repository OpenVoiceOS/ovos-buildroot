################################################################################
#
# python-ovos-ocp-bandcamp-plugin
#
################################################################################

PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_VERSION = b32203de979afbf0378d117ecf12f94820496d1d
PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-bandcamp-plugin,$(PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_VERSION))
PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_LICENSE_FILE = LICENSE
PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
