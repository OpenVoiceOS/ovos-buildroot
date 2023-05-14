################################################################################
#
# python-rich-click
#
################################################################################

PYTHON_RICH_CLICK_VERSION = 1.6.1
PYTHON_RICH_CLICK_SOURCE = rich-click-$(PYTHON_RICH_CLICK_VERSION).tar.gz
PYTHON_RICH_CLICK_SITE = https://files.pythonhosted.org/packages/8c/91/d1b210a5e3c3e076d55a2da815010d136cc2378c4bad6864b66b32de0c97
PYTHON_RICH_CLICK_SETUP_TYPE = setuptools

$(eval $(python-package))
