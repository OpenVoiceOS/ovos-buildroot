################################################################################
#
# python-ovos-vlc-plugin
#
################################################################################

PYTHON_OVOS_VLC_PLUGIN_VERSION = 1f6a2915d728baba925ecf5f53547ee7c7a766c1
PYTHON_OVOS_VLC_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-vlc-plugin,$(PYTHON_OVOS_VLC_PLUGIN_VERSION))
PYTHON_OVOS_VLC_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_VLC_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
