################################################################################
#
# python-msk
#
################################################################################

PYTHON_MSK_VERSION = 0.3.16
PYTHON_MSK_SOURCE = msk-$(PYTHON_MSK_VERSION).tar.gz
PYTHON_MSK_SITE = https://files.pythonhosted.org/packages/e3/2a/d90ef5bf2ddeee1b456bf82bc40ce816504299818eee9290ce6248b12433
PYTHON_MSK_SETUP_TYPE = setuptools

$(eval $(python-package))
