################################################################################
#
# python-feedparser
#
################################################################################

PYTHON_FEEDPARSER_VERSION = 6.0.2
PYTHON_FEEDPARSER_SOURCE = feedparser-$(PYTHON_FEEDPARSER_VERSION).tar.gz
PYTHON_FEEDPARSER_SITE = https://files.pythonhosted.org/packages/1b/84/934fc369d2e36d7fd9a196a72e68035cabc672c46bf7aa2661838e4d0ca9
PYTHON_FEEDPARSER_SETUP_TYPE = setuptools
PYTHON_FEEDPARSER_LICENSE = BSD-2-Clause
PYTHON_FEEDPARSER_LICENSE_FILES = LICENSE docs/license.rst

$(eval $(python-package))
