################################################################################
#
# python-pprintpp
#
################################################################################

PYTHON_PPRINTPP_VERSION = 0.4.0
PYTHON_PPRINTPP_SOURCE = pprintpp-$(PYTHON_PPRINTPP_VERSION).tar.gz
PYTHON_PPRINTPP_SITE = https://files.pythonhosted.org/packages/06/1a/7737e7a0774da3c3824d654993cf57adc915cb04660212f03406334d8c0b
PYTHON_PPRINTPP_SETUP_TYPE = setuptools
PYTHON_PPRINTPP_LICENSE = MIT
PYTHON_PPRINTPP_LICENSE_FILES = LICENSE

$(eval $(python-package))
