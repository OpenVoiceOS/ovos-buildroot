################################################################################
#
# python-ovos-backend-manager
#
################################################################################

PYTHON_OVOS_BACKEND_MANAGER_VERSION = 31d8fdd3b1eddcfdbfc53a60fe2a7769f8c241a9
PYTHON_OVOS_BACKEND_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-backend-manager,$(PYTHON_OVOS_BACKEND_MANAGER_VERSION))
PYTHON_OVOS_BACKEND_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_BACKEND_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
