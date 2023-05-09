################################################################################
#
# python-ovos-ocp-youtube-plugin
#
################################################################################

PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_VERSION = df6bfd8ccc3e178cfc5284c92932196883581dac
PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-youtube-plugin,$(PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_VERSION))
PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_LICENSE_YOUTUBE = LICENSE
PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
