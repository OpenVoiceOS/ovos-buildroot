################################################################################
#
# python-padacioso
#
################################################################################

PYTHON_PADACIOSO_VERSION = 02da04c52ab0eaf8e15e7ea1ff9a83bfc51533f6
PYTHON_PADACIOSO_SITE = $(call github,OpenVoiceOS,padacioso,$(PYTHON_PADACIOSO_VERSION))
PYTHON_PADACIOSO_SETUP_TYPE = setuptools
PYTHON_PADACIOSO_LICENSE = apache-2.0
PYTHON_PADACIOSO_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
