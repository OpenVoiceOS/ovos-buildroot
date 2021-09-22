################################################################################
#
# python-tailhead
#
################################################################################

PYTHON_TAILHEAD_VERSION = 1.0.2
PYTHON_TAILHEAD_SOURCE = tailhead-$(PYTHON_TAILHEAD_VERSION).tar.gz
PYTHON_TAILHEAD_SITE = https://files.pythonhosted.org/packages/17/ef/d07d5a05e490f1b2ef7e5914e61ea222165ae76356a701551a1fd24b1dfc
PYTHON_TAILHEAD_SETUP_TYPE = setuptools
PYTHON_TAILHEAD_LICENSE = MIT
PYTHON_TAILHEAD_LICENSE_FILES = LICENSE

$(eval $(python-package))
