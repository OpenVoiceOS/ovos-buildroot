################################################################################
#
# python-ifaddr
#
################################################################################

PYTHON_IFADDR_VERSION = 0.1.4
PYTHON_IFADDR_SOURCE = ifaddr-$(PYTHON_IFADDR_VERSION).zip
PYTHON_IFADDR_SITE = https://files.pythonhosted.org/packages/12/40/97ef30db32e0c798fc557af403ea263dbeae8d334571603f02e19f4021a0
PYTHON_IFADDR_SETUP_TYPE = setuptools

define PYTHON_IFADDR_EXTRACT_CMDS
        $(UNZIP) -d $(@D) $(DL_DIR)/python-ifaddr/$(PYTHON_IFADDR_SOURCE)
        mv $(@D)/ifaddr-$(PYTHON_IFADDR_VERSION)/* $(@D)
        $(RM) -r $(@D)/ifaddr-$(PYTHON_IFADDR_VERSION)
endef

$(eval $(python-package))
