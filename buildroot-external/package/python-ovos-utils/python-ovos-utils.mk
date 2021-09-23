################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = b4fba3732e99b5e41a5e0f0043fed24f6c8d9f84
PYTHON_OVOS_UTILS_SITE = $(call github,OpenVoiceOS,ovos_utils,$(PYTHON_OVOS_UTILS_VERSION))
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE

$(eval $(python-package))
