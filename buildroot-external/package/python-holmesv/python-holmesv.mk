################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 11036c18b6eb3425bf0ddab59cac3619195b193c
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
