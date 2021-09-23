################################################################################
#
# python-beniget
#
################################################################################

PYTHON_BENIGET_VERSION = 0.4.1
PYTHON_BENIGET_SOURCE = beniget-$(PYTHON_BENIGET_VERSION).tar.gz
PYTHON_BENIGET_SITE = https://files.pythonhosted.org/packages/14/e7/50cbac38f77eca8efd39516be6651fdb9f3c4c0fab8cf2cf05f612578737
PYTHON_BENIGET_SETUP_TYPE = setuptools
PYTHON_BENIGET_LICENSE = FIXME: please specify the exact BSD version
PYTHON_BENIGET_LICENSE_FILES = LICENSE

$(eval $(python-package))
$(eval $(host-python-package))
