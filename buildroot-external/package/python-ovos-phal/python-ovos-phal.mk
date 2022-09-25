################################################################################
#
# python-ovos-phal
#
################################################################################

PYTHON_OVOS_PHAL_VERSION = 867595c166a279b778718b6767f5ad2ccc605e75
PYTHON_OVOS_PHAL_SITE = $(call github,OpenVoiceOS,ovos_PHAL,$(PYTHON_OVOS_PHAL_VERSION))
PYTHON_OVOS_PHAL_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_LICENSE_FILES = LICENSE

$(eval $(python-package))
