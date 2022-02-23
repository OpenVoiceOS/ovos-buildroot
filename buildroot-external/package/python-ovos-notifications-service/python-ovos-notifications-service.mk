################################################################################
#
# python-ovos-notifications-service
#
################################################################################

PYTHON_OVOS_NOTIFICATIONS_SERVICE_VERSION = dc3f0572feab449dfc7dae51b4f11dc98d8464e6
PYTHON_OVOS_NOTIFICATIONS_SERVICE_SITE = $(call github,OpenVoiceOS,ovos_notifications_service,$(PYTHON_OVOS_NOTIFICATIONS_SERVICE_VERSION))
PYTHON_OVOS_NOTIFICATIONS_SERVICE_SETUP_TYPE = setuptools
PYTHON_OVOS_NOTIFICATIONS_SERVICE_LICENSE_FILES = LICENSE

$(eval $(python-package))
