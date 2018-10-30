################################################################################
#
# python-xxhash
#
################################################################################

PYTHON_XXHASH_VERSION = 1.2.0
PYTHON_XXHASH_SOURCE = xxhash-$(PYTHON_XXHASH_VERSION).tar.gz
PYTHON_XXHASH_SITE = https://files.pythonhosted.org/packages/72/b1/ed94f4a4ddaa899942295e69b7c478906d443a129c0c6eb032b18f91124b
PYTHON_XXHASH_SETUP_TYPE = setuptools
PYTHON_XXHASH_LICENSE = BSD-2-Clause, BSD-2-Clause
PYTHON_XXHASH_LICENSE_FILES = LICENSE deps/xxhash/LICENSE

$(eval $(python-package))
