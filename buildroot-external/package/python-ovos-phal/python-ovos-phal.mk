################################################################################
#
# python-ovos-phal
#
################################################################################

PYTHON_OVOS_PHAL_VERSION = b03fa1e3ba1202a34a755bb8979e0380419a02b3
PYTHON_OVOS_PHAL_SITE = $(call github,OpenVoiceOS,ovos_PHAL,$(PYTHON_OVOS_PHAL_VERSION))
PYTHON_OVOS_PHAL_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
