################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = f9a357490747975a7cc2c447f935938677f610b1
PYTHON_OVOS_LOCAL_BACKEND_SITE = $(call github,OpenVoiceOS,OVOS-local-backend,$(PYTHON_OVOS_LOCAL_BACKEND_VERSION))
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools

$(eval $(python-package))
