################################################################################
#
# python-padacioso
#
################################################################################

PYTHON_PADACIOSO_VERSION = 8888ffe95731edafad02e9603559abd24bb363a4
PYTHON_PADACIOSO_SITE = $(call github,OpenVoiceOS,padacioso,$(PYTHON_PADACIOSO_VERSION))
PYTHON_PADACIOSO_SETUP_TYPE = setuptools
PYTHON_PADACIOSO_LICENSE = apache-2.0
PYTHON_PADACIOSO_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
