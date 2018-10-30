################################################################################
#
# python-source
#
################################################################################

PYTHON_SOURCE_VERSION = 1.2.0
PYTHON_SOURCE_SOURCE = source-$(PYTHON_SOURCE_VERSION).zip
PYTHON_SOURCE_SITE = https://files.pythonhosted.org/packages/cd/44/8dfdedc238dbab3abacebbe4f76308847af8ff71bee20c668326b7941f76
PYTHON_SOURCE_SETUP_TYPE = distutils

define PYTHON_SOURCE_EXTRACT_CMDS
	$(UNZIP) -d $(@D) $(DL_DIR)/python-source/$(PYTHON_SOURCE_SOURCE)
	mv $(@D)/source-$(PYTHON_SOURCE_VERSION)/* $(@D)
	$(RM) -r $(@D)/source-$(PYTHON_SOURCE_VERSION)
endef

$(eval $(python-package))
