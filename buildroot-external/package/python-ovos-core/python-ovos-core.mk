################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = f1677edb2d8a1e9248f96d87f14a6731f6eb979f
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE
PYTHON_OVOS_CORE_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
