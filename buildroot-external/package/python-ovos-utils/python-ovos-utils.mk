################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = 07c024b871e7f5df05c546273fffa285f99c0e75
PYTHON_OVOS_UTILS_SITE = $(call github,OpenVoiceOS,ovos_utils,$(PYTHON_OVOS_UTILS_VERSION))
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE

$(eval $(python-package))
