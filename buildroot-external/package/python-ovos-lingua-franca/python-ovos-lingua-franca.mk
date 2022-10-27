################################################################################
#
# python-ovos-lingua-franca
#
################################################################################

PYTHON_OVOS_LINGUA_FRANCA_VERSION = 12ec4f8e1b31e91562f43193322a172111103b53
PYTHON_OVOS_LINGUA_FRANCA_SITE = $(call github,OpenVoiceOS,ovos-lingua-franca,$(PYTHON_OVOS_LINGUA_FRANCA_VERSION))
PYTHON_OVOS_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_OVOS_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_OVOS_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
