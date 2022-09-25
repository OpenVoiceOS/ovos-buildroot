################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = def54fbb413aa424da8b60320c93383833fef51e
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE

$(eval $(python-package))
