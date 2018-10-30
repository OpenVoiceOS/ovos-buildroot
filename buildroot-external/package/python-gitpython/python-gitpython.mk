################################################################################
#
# python-gitpython
#
################################################################################

PYTHON_GITPYTHON_VERSION = 2.1.11
PYTHON_GITPYTHON_SOURCE = GitPython-$(PYTHON_GITPYTHON_VERSION).tar.gz
PYTHON_GITPYTHON_SITE = https://files.pythonhosted.org/packages/4d/e8/98e06d3bc954e3c5b34e2a579ddf26255e762d21eb24fede458eff654c51
PYTHON_GITPYTHON_SETUP_TYPE = setuptools
PYTHON_GITPYTHON_LICENSE = BSD-3-Clause
PYTHON_GITPYTHON_LICENSE_FILES = LICENSE

$(eval $(python-package))
