################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = caa447f22250deb1cd368d324a33f1c32056e5f2
PYTHON_OVOS_LOCAL_BACKEND_SITE = $(call github,OpenVoiceOS,OVOS-local-backend,$(PYTHON_OVOS_LOCAL_BACKEND_VERSION))
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools
PYTHON_OVOS_LOCAL_BACKEND_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
