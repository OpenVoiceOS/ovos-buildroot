################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = 2dd1f844732e11e8ca2eee296e2a758c8276f875
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE
PYTHON_OVOS_CORE_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

PYTHON_OVOS_CORE_PRE_CONFIGURE_HOOKS = PYTHON_OVOS_CORE_REQUIREMENTS

define PYTHON_OVOS_CORE_REQUIREMENTS
	cp $(@D)/requirements/requirements.txt $(@D)/requirements/minimal.txt
endef

$(eval $(python-package))
