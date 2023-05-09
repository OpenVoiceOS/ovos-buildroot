################################################################################
#
# python-ovos-ocp-rss-plugin
#
################################################################################

PYTHON_OVOS_OCP_RSS_PLUGIN_VERSION = 3875c176609e29c925940366a8bafda0fb831ab7
PYTHON_OVOS_OCP_RSS_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-rss-plugin,$(PYTHON_OVOS_OCP_RSS_PLUGIN_VERSION))
PYTHON_OVOS_OCP_RSS_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_RSS_PLUGIN_LICENSE_FILE = LICENSE
PYTHON_OVOS_OCP_RSS_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
