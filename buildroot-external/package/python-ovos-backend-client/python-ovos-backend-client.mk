################################################################################
#
# python-ovos-backend-client
#
################################################################################

PYTHON_OVOS_BACKEND_CLIENT_VERSION = c10cc52430dbaa57d50121e2e120b5e39e8ccad1
PYTHON_OVOS_BACKEND_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-backend-client,$(PYTHON_OVOS_BACKEND_CLIENT_VERSION))
PYTHON_OVOS_BACKEND_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_BACKEND_CLIENT_LICENSE_FILES = LICENSE
PYTHON_OVOS_BACKEND_CLIENT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
