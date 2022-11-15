################################################################################
#
# python-ovos-phal-plugin-notification-widgets
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION = f5de7b75dc6f13f1670a0e9de77e88c51c56b1ea
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-notification-widgets,$(PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_LICENSE_FILES = LICENSE

$(eval $(python-package))
