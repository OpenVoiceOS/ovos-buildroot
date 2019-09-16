################################################################################
#
# python-padatious
#
################################################################################

PYTHON_PADATIOUS_VERSION = 0.4.6
PYTHON_PADATIOUS_SOURCE = padatious-$(PYTHON_PADATIOUS_VERSION).tar.gz
PYTHON_PADATIOUS_SITE = https://files.pythonhosted.org/packages/1f/37/0022764d88b1aacb7f42a9e3ba5250b10212d8b6cf6223c58e639d669a6c
PYTHON_PADATIOUS_SETUP_TYPE = setuptools

$(eval $(python-package))
