################################################################################
#
# python-flask-simplelogin
#
################################################################################

PYTHON_FLASK_SIMPLELOGIN_VERSION = 0.1.0
PYTHON_FLASK_SIMPLELOGIN_SOURCE = flask_simplelogin-$(PYTHON_FLASK_SIMPLELOGIN_VERSION).tar.gz
PYTHON_FLASK_SIMPLELOGIN_SITE = https://files.pythonhosted.org/packages/34/18/660cd00c6153dddefea29ae6a8274ab2a8bbb6b124fe4d23db944a6a079c
PYTHON_FLASK_SIMPLELOGIN_SETUP_TYPE = setuptools
PYTHON_FLASK_SIMPLELOGIN_LICENSE = MIT
PYTHON_FLASK_SIMPLELOGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
