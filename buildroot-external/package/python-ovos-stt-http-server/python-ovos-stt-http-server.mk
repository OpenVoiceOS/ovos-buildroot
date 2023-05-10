################################################################################
#
# python-ovos-stt-http-server
#
################################################################################

PYTHON_OVOS_STT_HTTP_SERVER_VERSION = 57c656242e44f8d1d4b60574775dc29167cf314f
PYTHON_OVOS_STT_HTTP_SERVER_SITE = $(call github,OpenVoiceOS,ovos-stt-http-server,$(PYTHON_OVOS_STT_HTTP_SERVER_VERSION))
PYTHON_OVOS_STT_HTTP_SERVER_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_HTTP_SERVER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
