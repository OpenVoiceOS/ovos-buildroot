################################################################################
#
# python-ovos-classifiers
#
################################################################################

PYTHON_OVOS_CLASSIFIERS_VERSION = 6010ddf63294f3b9e5ff3397b45a7201ddcc353f
PYTHON_OVOS_CLASSIFIERS_SITE = $(call github,OpenVoiceOS,ovos-classifiers,$(PYTHON_OVOS_CLASSIFIERS_VERSION))
PYTHON_OVOS_CLASSIFIERS_SETUP_TYPE = setuptools
PYTHON_OVOS_CLASSIFIERS_LICENSE_FILES = LICENSE
PYTHON_OVOS_CLASSIFIERS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
