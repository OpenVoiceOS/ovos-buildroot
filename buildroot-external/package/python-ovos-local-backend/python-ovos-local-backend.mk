################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = f181053e2592be94a66e622a963f1da99f4b0ee7
PYTHON_OVOS_LOCAL_BACKEND_SITE = $(call github,OpenVoiceOS,OVOS-local-backend,$(PYTHON_OVOS_LOCAL_BACKEND_VERSION))
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools

$(eval $(python-package))
