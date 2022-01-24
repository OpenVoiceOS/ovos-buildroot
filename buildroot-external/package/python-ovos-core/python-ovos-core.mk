################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = 05133a2f787df9cb7bc210b11d52d071d54aa06d
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE

$(eval $(python-package))
