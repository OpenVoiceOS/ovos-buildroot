################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = cf10eb22668651fc0e5545b3145c29c61d4de305
PYTHON_OVOS_UTILS_SITE = $(call github,OpenVoiceOS,ovos_utils,$(PYTHON_OVOS_UTILS_VERSION))
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE
PYTHON_OVOS_UTILS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
