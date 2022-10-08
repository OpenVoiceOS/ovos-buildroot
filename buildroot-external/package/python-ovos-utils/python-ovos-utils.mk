################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = 73b99a897738c973531fadb2739e4e4d0dcddc83
PYTHON_OVOS_UTILS_SITE = $(call github,OpenVoiceOS,ovos_utils,$(PYTHON_OVOS_UTILS_VERSION))
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE
PYTHON_OVOS_UTILS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
