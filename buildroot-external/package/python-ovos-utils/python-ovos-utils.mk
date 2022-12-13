################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = 8e0c4b762bc5b44c9f96ed6397cb996d53a7d598
PYTHON_OVOS_UTILS_SITE = $(call github,OpenVoiceOS,ovos_utils,$(PYTHON_OVOS_UTILS_VERSION))
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE
PYTHON_OVOS_UTILS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
