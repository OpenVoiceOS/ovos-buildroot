################################################################################
#
# python-lazy
#
################################################################################

PYTHON_LAZY_VERSION = 1.4
PYTHON_LAZY_SOURCE = lazy-$(PYTHON_LAZY_VERSION).zip
PYTHON_LAZY_SITE = https://files.pythonhosted.org/packages/ce/10/2c0cd8a601fff792f814b89233859e3fce2e266a5defd8af3bcadbe5c7ef
PYTHON_LAZY_SETUP_TYPE = setuptools
PYTHON_LAZY_LICENSE = BSD-2-Clause
PYTHON_LAZY_LICENSE_FILES = LICENSE

define PYTHON_LAZY_EXTRACT_CMDS
        $(UNZIP) -d $(@D) $(DL_DIR)/python-lazy/$(PYTHON_LAZY_SOURCE)
        mv $(@D)/lazy-$(PYTHON_LAZY_VERSION)/* $(@D)
        $(RM) -r $(@D)/lazy-$(PYTHON_LAZY_VERSION)
endef

$(eval $(python-package))
