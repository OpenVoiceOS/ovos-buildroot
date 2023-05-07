################################################################################
#
# python-ovos-backend-client
#
################################################################################

PYTHON_OVOS_BACKEND_CLIENT_VERSION = 1a746cee2fca3051415b51460a8a8f6897ee61da
PYTHON_OVOS_BACKEND_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-backend-client,$(PYTHON_OVOS_BACKEND_CLIENT_VERSION))
PYTHON_OVOS_BACKEND_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_BACKEND_CLIENT_LICENSE_FILES = LICENSE
PYTHON_OVOS_BACKEND_CLIENT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
