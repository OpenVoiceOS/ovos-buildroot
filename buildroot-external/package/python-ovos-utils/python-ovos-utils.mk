################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = 5bb8fb900cec3c8a233c4265dccecbe63c51a168
PYTHON_OVOS_UTILS_SITE = $(call github,OpenVoiceOS,ovos_utils,$(PYTHON_OVOS_UTILS_VERSION))
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE
PYTHON_OVOS_UTILS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
