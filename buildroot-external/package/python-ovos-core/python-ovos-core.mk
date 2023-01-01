################################################################################
#
# python-ovos-core
#
################################################################################

PYTHON_OVOS_CORE_VERSION = bcca687c6f66368246303a75b9686e02feebfe68
PYTHON_OVOS_CORE_SITE = $(call github,OpenVoiceOS,ovos-core,$(PYTHON_OVOS_CORE_VERSION))
PYTHON_OVOS_CORE_SETUP_TYPE = setuptools
PYTHON_OVOS_CORE_LICENSE_FILES = LICENSE
PYTHON_OVOS_CORE_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

PYTHON_OVOS_CORE_PRE_CONFIGURE_HOOKS = PYTHON_OVOS_CORE_REQUIREMENTS

define PYTHON_OVOS_CORE_REQUIREMENTS
	cp $(@D)/requirements/requirements.txt $(@D)/requirements/minimal.txt
endef

$(eval $(python-package))
