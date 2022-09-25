################################################################################
#
# python-selene-api
#
################################################################################

PYTHON_SELENE_API_VERSION = 8d11a9f8c6b0f7bb2877069506a330eb12da96e6
PYTHON_SELENE_API_SITE = $(call github,OpenVoiceOS,selene_api,$(PYTHON_SELENE_API_VERSION))
PYTHON_SELENE_API_SETUP_TYPE = setuptools
PYTHON_SELENE_API_LICENSE_FILES = LICENSE

$(eval $(python-package))
