################################################################################
#
# python-ovos-lingua-franca
#
################################################################################

PYTHON_OVOS_LINGUA_FRANCA_VERSION = 0d19598b9bd9df990247f78f33809ac56442db7c
PYTHON_OVOS_LINGUA_FRANCA_SITE = $(call github,OpenVoiceOS,ovos-lingua-franca,$(PYTHON_OVOS_LINGUA_FRANCA_VERSION))
PYTHON_OVOS_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_OVOS_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_OVOS_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
