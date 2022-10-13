################################################################################
#
# python-ovos-backend-client
#
################################################################################

PYTHON_OVOS_BACKEND_CLIENT_VERSION = c7d6e455312d1d0f9f188c6907cc85ba1ebd8440
PYTHON_OVOS_BACKEND_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-backend-client,$(PYTHON_OVOS_BACKEND_CLIENT_VERSION))
PYTHON_OVOS_BACKEND_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_BACKEND_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
