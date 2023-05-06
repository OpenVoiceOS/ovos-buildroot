################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_MESSAGEBUS_VERSION = 034ef0b14aeab33152fc97b3fea0e445051a828a
PYTHON_OVOS_MESSAGEBUS_SITE = $(call github,OpenVoiceOS,ovos-messagebus,$(PYTHON_OVOS_MESSAGEBUS_VERSION))
PYTHON_OVOS_MESSAGEBUS_SETUP_TYPE = setuptools
PYTHON_OVOS_MESSAGEBUS_LICENSE_FILES = LICENSE
PYTHON_OVOS_MESSAGEBUS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
