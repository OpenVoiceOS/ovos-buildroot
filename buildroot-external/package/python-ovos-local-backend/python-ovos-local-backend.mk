################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = 26e47638ebd941a6dcadc11c333eb2179cbd8182
PYTHON_OVOS_LOCAL_BACKEND_SITE = $(call github,OpenVoiceOS,OVOS-local-backend,$(PYTHON_OVOS_LOCAL_BACKEND_VERSION))
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools

$(eval $(python-package))
