################################################################################
#
# python-ovos-classifiers
#
################################################################################

PYTHON_OVOS_CLASSIFIERS_VERSION = 67ac7258aa933250d16761995ab439b27d28d2d3
PYTHON_OVOS_CLASSIFIERS_SITE = $(call github,OpenVoiceOS,ovos-classifiers,$(PYTHON_OVOS_CLASSIFIERS_VERSION))
PYTHON_OVOS_CLASSIFIERS_SETUP_TYPE = setuptools
PYTHON_OVOS_CLASSIFIERS_LICENSE_FILES = LICENSE
PYTHON_OVOS_CLASSIFIERS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
