################################################################################
#
# python-wikipedia-for-humans
#
################################################################################

PYTHON_WIKIPEDIA_FOR_HUMANS_VERSION = 0.3.0
PYTHON_WIKIPEDIA_FOR_HUMANS_SOURCE = wikipedia_for_humans-$(PYTHON_WIKIPEDIA_FOR_HUMANS_VERSION).tar.gz
PYTHON_WIKIPEDIA_FOR_HUMANS_SITE = https://files.pythonhosted.org/packages/ef/f3/ceb5e80ad2faa5c18697dc64d7f1ea68bf94faf995def69eeb37b5a20c22
PYTHON_WIKIPEDIA_FOR_HUMANS_SETUP_TYPE = setuptools
PYTHON_WIKIPEDIA_FOR_HUMANS_LICENSE = MIT

$(eval $(python-package))
