################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = a04aafb682c67dbc50e79a81ce4cdeab99e8d824
PYTHON_OVOS_LOCAL_BACKEND_SITE = $(call github,OpenVoiceOS,OVOS-local-backend,$(PYTHON_OVOS_LOCAL_BACKEND_VERSION))
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools

$(eval $(python-package))
