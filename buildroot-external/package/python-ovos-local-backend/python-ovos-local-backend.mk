################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = c1dedabcf272f1c426adc83684006d7194f09d07
PYTHON_OVOS_LOCAL_BACKEND_SITE = $(call github,OpenVoiceOS,OVOS-local-backend,$(PYTHON_OVOS_LOCAL_BACKEND_VERSION))
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools
PYTHON_OVOS_LOCAL_BACKEND_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
