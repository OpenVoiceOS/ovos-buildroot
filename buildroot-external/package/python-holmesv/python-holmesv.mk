################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = f1a3474b89285cd48abbe5f1fccbe7a00f2d9d92
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
