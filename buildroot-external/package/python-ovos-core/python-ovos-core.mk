################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = 348535cd993a755fe91b358f5a0694a3f788d226
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE

$(eval $(python-package))
