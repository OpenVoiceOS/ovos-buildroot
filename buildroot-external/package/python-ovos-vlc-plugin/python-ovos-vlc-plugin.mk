################################################################################
#
# python-ovos-vlc-plugin
#
################################################################################

PYTHON_OVOS_VLC_PLUGIN_VERSION = f440a4b40f54e15d26eda1171a8308983f34ebc1
PYTHON_OVOS_VLC_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-vlc-plugin,$(PYTHON_OVOS_VLC_PLUGIN_VERSION))
PYTHON_OVOS_VLC_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_VLC_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
