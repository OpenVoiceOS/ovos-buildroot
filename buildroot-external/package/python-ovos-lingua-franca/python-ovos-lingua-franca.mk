################################################################################
#
# python-ovos-lingua-franca
#
################################################################################

PYTHON_OVOS_LINGUA_FRANCA_VERSION = 0c4ead9b3ad396fc68a5b5c6465678b567c6c01f
PYTHON_OVOS_LINGUA_FRANCA_SITE = $(call github,OpenVoiceOS,ovos-lingua-franca,$(PYTHON_OVOS_LINGUA_FRANCA_VERSION))
PYTHON_OVOS_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_OVOS_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_OVOS_LINGUA_FRANCA_LICENSE_FILES = LICENSE
PYTHON_OVOS_LINGUA_FRANCA_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
