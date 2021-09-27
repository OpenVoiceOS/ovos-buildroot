################################################################################
#
# python-gast
#
################################################################################

PYTHON_GAST_VERSION = 0.5.2
PYTHON_GAST_SOURCE = gast-$(PYTHON_GAST_VERSION).tar.gz
PYTHON_GAST_SITE = https://files.pythonhosted.org/packages/53/88/e12484298c9c913b68c1de191fa673f8a976036d98efbdcb60014f14c65c
PYTHON_GAST_SETUP_TYPE = setuptools
PYTHON_GAST_LICENSE = FIXME: please specify the exact BSD version
PYTHON_GAST_LICENSE_FILES = LICENSE

$(eval $(python-package))
$(eval $(host-python-package))
