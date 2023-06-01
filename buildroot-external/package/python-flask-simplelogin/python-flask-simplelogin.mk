################################################################################
#
# python-flask-simplelogin
#
################################################################################

PYTHON_FLASK_SIMPLELOGIN_VERSION = 0.1.2
PYTHON_FLASK_SIMPLELOGIN_SOURCE = flask_simplelogin-$(PYTHON_FLASK_SIMPLELOGIN_VERSION).tar.gz
PYTHON_FLASK_SIMPLELOGIN_SITE = https://files.pythonhosted.org/packages/e3/9b/942c42c1122e502e0bea52ac96230591df3bf58369de11ad3ad2e0c448d3
PYTHON_FLASK_SIMPLELOGIN_SETUP_TYPE = setuptools
PYTHON_FLASK_SIMPLELOGIN_LICENSE = MIT
PYTHON_FLASK_SIMPLELOGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
