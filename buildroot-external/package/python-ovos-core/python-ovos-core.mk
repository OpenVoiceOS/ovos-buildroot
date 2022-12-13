################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = dc960e7bf7afc33f53e5c918a08049b20745df47
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE

$(eval $(python-package))
