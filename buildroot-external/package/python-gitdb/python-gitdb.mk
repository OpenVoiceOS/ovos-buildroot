################################################################################
#
# python-gitdb
#
################################################################################

PYTHON_GITDB_VERSION = 4.0.5
PYTHON_GITDB_SOURCE = gitdb-$(PYTHON_GITDB_VERSION).tar.gz
PYTHON_GITDB_SITE = https://files.pythonhosted.org/packages/d1/05/eaf2ac564344030d8b3ce870b116d7bb559020163e80d9aa4a3d75f3e820
PYTHON_GITDB_SETUP_TYPE = setuptools
PYTHON_GITDB_LICENSE = BSD-3-Clause
PYTHON_GITDB_LICENSE_FILES = LICENSE

$(eval $(python-package))
