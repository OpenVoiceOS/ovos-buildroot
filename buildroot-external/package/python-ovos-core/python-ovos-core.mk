################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = 79185d366fd3ad89a0a9d7f180ec5f6ec1f3d4b7
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE
PYTHON_OVOS_CORE_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
