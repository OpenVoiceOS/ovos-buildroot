################################################################################
#
# python-padatious
#
################################################################################

PYTHON_PADATIOUS_VERSION = 0.4.8
PYTHON_PADATIOUS_SOURCE = padatious-$(PYTHON_PADATIOUS_VERSION).tar.gz
PYTHON_PADATIOUS_SITE = https://files.pythonhosted.org/packages/d0/e7/70a6eb34b7e67fef5b2645df2ee1f807db2b5a345e4e6adfb2660a56425b
PYTHON_PADATIOUS_SETUP_TYPE = setuptools

$(eval $(python-package))
