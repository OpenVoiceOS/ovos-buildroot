################################################################################
#
# python-ovos-stt-http-server
#
################################################################################

PYTHON_OVOS_STT_HTTP_SERVER_VERSION = f21f946c94bc512adc44573da54a865fd83c9af3
PYTHON_OVOS_STT_HTTP_SERVER_SITE = $(call github,OpenVoiceOS,ovos-stt-http-server,$(PYTHON_OVOS_STT_HTTP_SERVER_VERSION))
PYTHON_OVOS_STT_HTTP_SERVER_SETUP_TYPE = setuptools

$(eval $(python-package))
