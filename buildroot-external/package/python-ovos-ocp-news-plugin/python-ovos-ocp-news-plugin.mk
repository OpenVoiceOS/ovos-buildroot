################################################################################
#
# python-ovos-ocp-news-plugin
#
################################################################################

PYTHON_OVOS_OCP_NEWS_PLUGIN_VERSION = 758a5c052aa5c6682e6593950a9c0bdf3f621d62
PYTHON_OVOS_OCP_NEWS_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-news-plugin,$(PYTHON_OVOS_OCP_NEWS_PLUGIN_VERSION))
PYTHON_OVOS_OCP_NEWS_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_NEWS_PLUGIN_LICENSE_FILE = LICENSE
PYTHON_OVOS_OCP_NEWS_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
