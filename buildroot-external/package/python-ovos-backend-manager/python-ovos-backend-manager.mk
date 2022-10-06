################################################################################
#
# python-ovos-backend-manager
#
################################################################################

PYTHON_OVOS_BACKEND_MANAGER_VERSION = d56534e8a39137e0aa4ec714a88708b1dca8bf84
PYTHON_OVOS_BACKEND_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-backend-manager,$(PYTHON_OVOS_BACKEND_MANAGER_VERSION))
PYTHON_OVOS_BACKEND_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_BACKEND_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
