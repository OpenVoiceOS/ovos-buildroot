################################################################################
#
# python-humanhash3
#
################################################################################

PYTHON_HUMANHASH3_VERSION = 0.0.6
PYTHON_HUMANHASH3_SOURCE = humanhash3-$(PYTHON_HUMANHASH3_VERSION).tar.gz
PYTHON_HUMANHASH3_SITE = https://files.pythonhosted.org/packages/01/06/733ffbb45b78c34eba21d72e71a67f44af6efcdfb2e31ccaa837eb5144be
PYTHON_HUMANHASH3_SETUP_TYPE = distutils

$(eval $(python-package))
