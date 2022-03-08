################################################################################
#
# python-ovos-lingua-franca
#
################################################################################

PYTHON_OVOS_LINGUA_FRANCA_VERSION = e5ab15963ea9827f85c2f9cfc4cf14f7401307bf
PYTHON_OVOS_LINGUA_FRANCA_SITE = $(call github,OpenVoiceOS,ovos-lingua-franca,$(PYTHON_OVOS_LINGUA_FRANCA_VERSION))
PYTHON_OVOS_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_OVOS_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_OVOS_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
