################################################################################
#
# python-wikipedia-api
#
################################################################################

PYTHON_WIKIPEDIA_API_VERSION = 0.5.4
PYTHON_WIKIPEDIA_API_SOURCE = Wikipedia-API-$(PYTHON_WIKIPEDIA_API_VERSION).tar.gz
PYTHON_WIKIPEDIA_API_SITE = https://files.pythonhosted.org/packages/ef/3d/289963bbf51f8d00cdf7483cdc2baee25ba877e8b4eb72157c47211e3b57
PYTHON_WIKIPEDIA_API_SETUP_TYPE = setuptools
PYTHON_WIKIPEDIA_API_LICENSE = MIT
PYTHON_WIKIPEDIA_API_LICENSE_FILES = LICENSE

$(eval $(python-package))
