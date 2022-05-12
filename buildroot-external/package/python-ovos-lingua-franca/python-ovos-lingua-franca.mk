################################################################################
#
# python-ovos-lingua-franca
#
################################################################################

PYTHON_OVOS_LINGUA_FRANCA_VERSION = 392cc37cbfde3b8d6f11258c1e148e63ba2fb951
PYTHON_OVOS_LINGUA_FRANCA_SITE = $(call github,OpenVoiceOS,ovos-lingua-franca,$(PYTHON_OVOS_LINGUA_FRANCA_VERSION))
PYTHON_OVOS_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_OVOS_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_OVOS_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
