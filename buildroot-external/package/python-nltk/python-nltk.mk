################################################################################
#
# python-nltk
#
################################################################################

PYTHON_NLTK_VERSION = 3.8.1
PYTHON_NLTK_SOURCE = nltk-$(PYTHON_NLTK_VERSION).zip
PYTHON_NLTK_SITE = https://files.pythonhosted.org/packages/57/49/51af17a2b0d850578d0022408802aa452644d40281a6c6e82f7cb0235ddb
PYTHON_NLTK_SETUP_TYPE = setuptools
PYTHON_NLTK_LICENSE = Apache-2.0
PYTHON_NLTK_LICENSE_FILES = LICENSE.txt

define PYTHON_NLTK_EXTRACT_CMDS
        $(UNZIP) -d $(@D) $(DL_DIR)/python-nltk/$(PYTHON_NLTK_SOURCE)
        mv $(@D)/nltk-$(PYTHON_NLTK_VERSION)/* $(@D)
        $(RM) -r $(@D)/nltk-$(PYTHON_NLTK_VERSION)
endef

$(eval $(python-package))
