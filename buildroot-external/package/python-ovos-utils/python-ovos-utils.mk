################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = ba0e2297e7e0c307c7ec23f654207648234ff67a
PYTHON_OVOS_UTILS_SITE = $(call github,OpenVoiceOS,ovos_utils,$(PYTHON_OVOS_UTILS_VERSION))
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE

$(eval $(python-package))
