################################################################################
#
# python-gitpython
#
################################################################################

PYTHON_GITPYTHON_VERSION = 3.1.2
PYTHON_GITPYTHON_SOURCE = GitPython-$(PYTHON_GITPYTHON_VERSION).tar.gz
PYTHON_GITPYTHON_SITE = https://files.pythonhosted.org/packages/36/5d/23c3f9a527a1e1c79e8622c7bb74704f6468351cd756e20f65f2ea7aba44
PYTHON_GITPYTHON_SETUP_TYPE = setuptools
PYTHON_GITPYTHON_LICENSE = BSD-3-Clause
PYTHON_GITPYTHON_LICENSE_FILES = LICENSE

$(eval $(python-package))
