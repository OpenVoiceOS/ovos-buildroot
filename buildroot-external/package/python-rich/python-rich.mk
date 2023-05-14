################################################################################
#
# python-rich
#
################################################################################

PYTHON_RICH_VERSION = 13.3.5
PYTHON_RICH_SOURCE = rich-$(PYTHON_RICH_VERSION).tar.gz
PYTHON_RICH_SITE = https://files.pythonhosted.org/packages/3d/0b/8dd34d20929c4b5e474db2e64426175469c2b7fea5ba71c6d4b3397a9729
PYTHON_RICH_SETUP_TYPE = setuptools

$(eval $(python-package))
