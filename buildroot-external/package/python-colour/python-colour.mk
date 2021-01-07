################################################################################
#
# python-colour
#
################################################################################

PYTHON_COLOUR_VERSION = 0.1.5
PYTHON_COLOUR_SOURCE = colour-$(PYTHON_COLOUR_VERSION).tar.gz
PYTHON_COLOUR_SITE = https://files.pythonhosted.org/packages/a0/d4/5911a7618acddc3f594ddf144ecd8a03c29074a540f4494670ad8f153efe
PYTHON_COLOUR_SETUP_TYPE = setuptools

$(eval $(python-package))
