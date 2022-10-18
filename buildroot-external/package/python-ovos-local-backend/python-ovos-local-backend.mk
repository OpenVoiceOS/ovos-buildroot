################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = ea56f6ef600864c4c9ca082654b1cbb550e31e44
PYTHON_OVOS_LOCAL_BACKEND_SITE = $(call github,OpenVoiceOS,OVOS-local-backend,$(PYTHON_OVOS_LOCAL_BACKEND_VERSION))
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools
PYTHON_OVOS_LOCAL_BACKEND_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
