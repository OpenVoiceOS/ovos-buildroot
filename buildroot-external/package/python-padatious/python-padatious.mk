################################################################################
#
# python-padatious
#
################################################################################

PYTHON_PADATIOUS_VERSION = 0.4.5
PYTHON_PADATIOUS_SOURCE = padatious-$(PYTHON_PADATIOUS_VERSION).tar.gz
PYTHON_PADATIOUS_SITE = https://files.pythonhosted.org/packages/00/ca/5d2262ec5ca90afa94706b78c770de9f48298d3048cd65dc0ad79ffcfb10
PYTHON_PADATIOUS_SETUP_TYPE = setuptools

$(eval $(python-package))
