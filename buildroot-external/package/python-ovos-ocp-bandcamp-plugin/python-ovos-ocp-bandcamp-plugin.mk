################################################################################
#
# python-ovos-ocp-bandcamp-plugin
#
################################################################################

PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_VERSION = d619878659a87fc6a383444164aa8dcfe384d0c4
PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-bandcamp-plugin,$(PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_VERSION))
PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_LICENSE_FILE = LICENSE
PYTHON_OVOS_OCP_BANDCAMP_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
