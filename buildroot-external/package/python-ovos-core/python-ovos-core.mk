################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = 60828025d7040b7b953f7c1e1c7e25410f882df9
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE

$(eval $(python-package))
