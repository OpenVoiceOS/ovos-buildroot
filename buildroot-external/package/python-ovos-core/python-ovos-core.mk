################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = e4cabf257c278e183d5c77aaaa3c920028e4f51f
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE
PYTHON_OVOS_CORE_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
