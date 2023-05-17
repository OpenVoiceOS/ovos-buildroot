################################################################################
#
# python-padacioso
#
################################################################################

PYTHON_PADACIOSO_VERSION = dbca43925f35e3b3b682800520be8a678f3f2bc5
PYTHON_PADACIOSO_SITE = $(call github,OpenVoiceOS,padacioso,$(PYTHON_PADACIOSO_VERSION))
PYTHON_PADACIOSO_SETUP_TYPE = setuptools
PYTHON_PADACIOSO_LICENSE = apache-2.0
PYTHON_PADACIOSO_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
