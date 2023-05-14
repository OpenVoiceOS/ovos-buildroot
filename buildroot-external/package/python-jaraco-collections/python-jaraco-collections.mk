################################################################################
#
# python-jaraco-collections
#
################################################################################

PYTHON_JARACO_COLLECTIONS_VERSION = 4.1.0
PYTHON_JARACO_COLLECTIONS_SOURCE = jaraco.collections-$(PYTHON_JARACO_COLLECTIONS_VERSION).tar.gz
PYTHON_JARACO_COLLECTIONS_SITE = https://files.pythonhosted.org/packages/39/5f/3d235b6c12b117c7bc0d96a2bc6ab6bdac00567f8e595729a0cfe14994a7
PYTHON_JARACO_COLLECTIONS_LICENSE = MIT
PYTHON_JARACO_COLLECTIONS_LICENSE_FILES = LICENSE
PYTHON_JARACO_COLLECTIONS_SETUP_TYPE = setuptools
PYTHON_JARACO_COLLECTIONS_DEPENDENCIES = host-python-setuptools-scm

$(eval $(python-package))
