################################################################################
#
# python-ovos-phal-plugin-notification-widgets
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION = 9f881ef4cc679758f5ed1417af1b871747071c7b
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-notification-widgets,$(PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_LICENSE_FILES = LICENSE

$(eval $(python-package))
