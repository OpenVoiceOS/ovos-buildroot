################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 98c669d4eaa38cb7173b84d718e941315b903729
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
