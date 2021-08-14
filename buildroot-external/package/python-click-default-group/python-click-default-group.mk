################################################################################
#
# python-click-default-group
#
################################################################################

PYTHON_CLICK_DEFAULT_GROUP_VERSION = 1.2.2
PYTHON_CLICK_DEFAULT_GROUP_SOURCE = click-default-group-$(PYTHON_CLICK_DEFAULT_GROUP_VERSION).tar.gz
PYTHON_CLICK_DEFAULT_GROUP_SITE = https://files.pythonhosted.org/packages/22/3a/e9feb3435bd4b002d183fcb9ee08fb369a7e570831ab1407bc73f079948f
PYTHON_CLICK_DEFAULT_GROUP_SETUP_TYPE = setuptools
PYTHON_CLICK_DEFAULT_GROUP_LICENSE = Public Domain

$(eval $(python-package))
