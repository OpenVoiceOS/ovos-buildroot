################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 302277ec47185e1728ca7b08ef8a647d1102c585
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
