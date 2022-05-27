################################################################################
#
# python-ovos-phal-plugin-notification-widgets
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION = 5e8764e7a15c28c1ff3086c39d22152f0ef342af
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-notification-widgets,$(PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_LICENSE_FILES = LICENSE

$(eval $(python-package))
