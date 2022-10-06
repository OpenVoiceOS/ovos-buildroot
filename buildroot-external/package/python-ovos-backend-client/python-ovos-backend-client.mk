################################################################################
#
# python-ovos-backend-client
#
################################################################################

PYTHON_OVOS_BACKEND_CLIENT_VERSION = 8b95d72a8e1d100d34f2a7473e2e8cf235181ef7
PYTHON_OVOS_BACKEND_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-backend-client,$(PYTHON_OVOS_BACKEND_CLIENT_VERSION))
PYTHON_OVOS_BACKEND_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_BACKEND_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
