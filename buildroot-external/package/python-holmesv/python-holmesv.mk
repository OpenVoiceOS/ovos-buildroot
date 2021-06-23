################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 5712518f13286a06ffe2921d746bdb20a04a06f0
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
