################################################################################
#
# python-olefile
#
################################################################################

PYTHON_OLEFILE_VERSION = 0.46
PYTHON_OLEFILE_SOURCE = olefile-$(PYTHON_OLEFILE_VERSION).zip
PYTHON_OLEFILE_SITE = https://files.pythonhosted.org/packages/34/81/e1ac43c6b45b4c5f8d9352396a14144bba52c8fec72a80f425f6a4d653ad
PYTHON_OLEFILE_SETUP_TYPE = setuptools
PYTHON_OLEFILE_LICENSE_FILES = LICENSE.txt doc/License.rst

define PYTHON_OLEFILE_EXTRACT_CMDS
	$(UNZIP) -d $(@D) $(DL_DIR)/python-olefile/$(PYTHON_OLEFILE_SOURCE)
	mv $(@D)/olefile-$(PYTHON_OLEFILE_VERSION)/* $(@D)
	$(RM) -r $(@D)/olefile-$(PYTHON_OLEFILE_VERSION)
endef

$(eval $(python-package))
