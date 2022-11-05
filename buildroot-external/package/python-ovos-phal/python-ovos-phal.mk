################################################################################
#
# python-ovos-phal
#
################################################################################

PYTHON_OVOS_PHAL_VERSION = d11a56f817ca1f67750da56f6f826a68566f3911
PYTHON_OVOS_PHAL_SITE = $(call github,OpenVoiceOS,ovos_PHAL,$(PYTHON_OVOS_PHAL_VERSION))
PYTHON_OVOS_PHAL_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_LICENSE_FILES = LICENSE

$(eval $(python-package))
