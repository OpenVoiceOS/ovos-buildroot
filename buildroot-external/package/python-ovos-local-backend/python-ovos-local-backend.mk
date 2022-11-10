################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = d4e3247dee2fa730e3511c1e84faa956ce7846ed
PYTHON_OVOS_LOCAL_BACKEND_SITE = $(call github,OpenVoiceOS,OVOS-local-backend,$(PYTHON_OVOS_LOCAL_BACKEND_VERSION))
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools
PYTHON_OVOS_LOCAL_BACKEND_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
