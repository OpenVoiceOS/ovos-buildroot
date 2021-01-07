################################################################################
#
# python-astral
#
################################################################################

PYTHON_ASTRAL_VERSION = 1.4
PYTHON_ASTRAL_SOURCE = astral-$(PYTHON_ASTRAL_VERSION).zip
PYTHON_ASTRAL_SITE = https://files.pythonhosted.org/packages/a4/d6/c309f266677372964c6002a56a7bec2a90875338a71325e20b24d6d1e187
PYTHON_ASTRAL_DEPENDENCIES = host-python-pytz
PYTHON_ASTRAL_SETUP_TYPE = setuptools
PYTHON_ASTRAL_LICENSE = Apache-2.0
PYTHON_ASTRAL_LICENSE_FILES = LICENSE

define PYTHON_ASTRAL_EXTRACT_CMDS
        $(UNZIP) -d $(@D) $(DL_DIR)/python-astral/$(PYTHON_ASTRAL_SOURCE)
        mv $(@D)/astral-$(PYTHON_ASTRAL_VERSION)/* $(@D)
        $(RM) -r $(@D)/astral-$(PYTHON_ASTRAL_VERSION)
endef

$(eval $(python-package))
