################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 889c25a613db7c5af02a3139f9b109584928cd6b
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
