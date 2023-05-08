################################################################################
#
# python-ovos-personal-backend
#
################################################################################

PYTHON_OVOS_PERSONAL_BACKEND_VERSION = 5029f4bd5a97fafd47590ca35757f579e64f53d4
PYTHON_OVOS_PERSONAL_BACKEND_SITE = $(call github,OpenVoiceOS,ovos-personal-backend,$(PYTHON_OVOS_PERSONAL_BACKEND_VERSION))
PYTHON_OVOS_PERSONAL_BACKEND_SETUP_TYPE = setuptools
PYTHON_OVOS_PERSONAL_BACKEND_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
