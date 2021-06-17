################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = bd0301d76fa1a57b15c9991d4b4c39504861f2ed
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
