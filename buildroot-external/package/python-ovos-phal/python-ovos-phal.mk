################################################################################
#
# python-ovos-phal
#
################################################################################

PYTHON_OVOS_PHAL_VERSION = 7c68e331707678f650c6083bb1594664021ca95a
PYTHON_OVOS_PHAL_SITE = $(call github,OpenVoiceOS,ovos_PHAL,$(PYTHON_OVOS_PHAL_VERSION))
PYTHON_OVOS_PHAL_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_LICENSE_FILES = LICENSE

$(eval $(python-package))
