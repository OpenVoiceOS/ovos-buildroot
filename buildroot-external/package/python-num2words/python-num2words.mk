################################################################################
#
# python-num2words
#
################################################################################

PYTHON_NUM2WORDS_VERSION = 0.5.10
PYTHON_NUM2WORDS_SOURCE = num2words-$(PYTHON_NUM2WORDS_VERSION).tar.gz
PYTHON_NUM2WORDS_SITE = https://files.pythonhosted.org/packages/33/db/76f1151a1b0cfad532d41021b77cd231495bf72c47618166f92dcdff2ebe
PYTHON_NUM2WORDS_SETUP_TYPE = setuptools
PYTHON_NUM2WORDS_LICENSE = GNU Library or Lesser General Public License (LGPL)
PYTHON_NUM2WORDS_LICENSE_FILES = COPYING

$(eval $(python-package))
