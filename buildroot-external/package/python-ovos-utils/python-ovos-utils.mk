################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = cc7550b65aec51ece9319b90aedb1b5604faddb7
PYTHON_OVOS_UTILS_SITE = $(call github,OpenVoiceOS,ovos_utils,$(PYTHON_OVOS_UTILS_VERSION))
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE
PYTHON_OVOS_UTILS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
