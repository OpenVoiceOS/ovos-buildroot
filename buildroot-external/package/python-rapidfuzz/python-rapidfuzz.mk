################################################################################
#
# python-rapidfuzz
#
################################################################################

PYTHON_RAPIDFUZZ_VERSION = 1.4.1
PYTHON_RAPIDFUZZ_SOURCE = rapidfuzz-$(PYTHON_RAPIDFUZZ_VERSION).tar.gz
PYTHON_RAPIDFUZZ_SITE = https://files.pythonhosted.org/packages/2f/86/cc342a061f0ae579b31376f23afd737a4a7cf34dfa9199859646cb4a941b
PYTHON_RAPIDFUZZ_SETUP_TYPE = setuptools
PYTHON_RAPIDFUZZ_LICENSE = Apache-2.0
PYTHON_RAPIDFUZZ_LICENSE_FILES = LICENSE

$(eval $(python-package))
