################################################################################
#
# python-pako
#
################################################################################

PYTHON_PAKO_VERSION = 0.2.3
PYTHON_PAKO_SOURCE = pako-$(PYTHON_PAKO_VERSION).tar.gz
PYTHON_PAKO_SITE = https://files.pythonhosted.org/packages/96/91/bf16a2f64a6628dfbfd9218f0331fbf73655530608ddd2f8fb597fdb9458
PYTHON_PAKO_SETUP_TYPE = setuptools
PYTHON_PAKO_LICENSE = Apache-2.0
PYTHON_PAKO_LICENSE_FILES = LICENSE

$(eval $(python-package))
