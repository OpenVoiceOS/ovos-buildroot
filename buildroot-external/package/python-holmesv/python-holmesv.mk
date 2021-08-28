################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 2a8bcf0a291cfa20ab68a767081ee69fe8037f29
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
