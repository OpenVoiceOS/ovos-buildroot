################################################################################
#
# python-pako
#
################################################################################

PYTHON_PAKO_VERSION = 0.3.1
PYTHON_PAKO_SOURCE = pako-$(PYTHON_PAKO_VERSION).tar.gz
PYTHON_PAKO_SITE = https://files.pythonhosted.org/packages/0d/27/0c491946572618f32c174101facca4dfb7034317e045c1e3950ed4fee689
PYTHON_PAKO_SETUP_TYPE = setuptools
PYTHON_PAKO_LICENSE = Apache-2.0
PYTHON_PAKO_LICENSE_FILES = LICENSE

$(eval $(python-package))
