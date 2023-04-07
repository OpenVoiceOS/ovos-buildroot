################################################################################
#
# python-rapidfuzz
#
################################################################################

PYTHON_RAPIDFUZZ_VERSION = 2.15.0
PYTHON_RAPIDFUZZ_SOURCE = rapidfuzz-$(PYTHON_RAPIDFUZZ_VERSION).tar.gz
PYTHON_RAPIDFUZZ_SITE = https://files.pythonhosted.org/packages/01/8c/cad170708243488e2b2a2e727eb40f30018231efa7fa1a9a3a3dc82d9f42
PYTHON_RAPIDFUZZ_SETUP_TYPE = setuptools
PYTHON_RAPIDFUZZ_LICENSE = Apache-2.0
PYTHON_RAPIDFUZZ_LICENSE_FILES = LICENSE

$(eval $(python-package))
