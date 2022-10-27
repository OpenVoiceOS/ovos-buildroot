################################################################################
#
# python-ovos-phal
#
################################################################################

PYTHON_OVOS_PHAL_VERSION = 0c7257f240ba9139b778c0670cf6a983b6aa18bd
PYTHON_OVOS_PHAL_SITE = $(call github,OpenVoiceOS,ovos_PHAL,$(PYTHON_OVOS_PHAL_VERSION))
PYTHON_OVOS_PHAL_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_LICENSE_FILES = LICENSE

$(eval $(python-package))
