################################################################################
#
# python-ovos-backend-client
#
################################################################################

PYTHON_OVOS_BACKEND_CLIENT_VERSION = 37869f7bce29b22a40530f53938a848c6014a512
PYTHON_OVOS_BACKEND_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-backend-client,$(PYTHON_OVOS_BACKEND_CLIENT_VERSION))
PYTHON_OVOS_BACKEND_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_BACKEND_CLIENT_LICENSE_FILES = LICENSE
PYTHON_OVOS_BACKEND_CLIENT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
