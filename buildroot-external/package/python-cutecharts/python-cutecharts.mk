################################################################################
#
# python-cutecharts
#
################################################################################

PYTHON_CUTECHARTS_VERSION = 4a995adb7f6851517f29c9ac23cfe717666d4cd6
PYTHON_CUTECHARTS_SITE = $(call github,cutecharts,cutecharts.py,$(PYTHON_CUTECHARTS_VERSION))
PYTHON_CUTECHARTS_SETUP_TYPE = setuptools
PYTHON_CUTECHARTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
