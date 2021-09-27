################################################################################
#
# python-flask-fontawesome
#
################################################################################

PYTHON_FLASK_FONTAWESOME_VERSION = 0.1.5
PYTHON_FLASK_FONTAWESOME_SOURCE = Flask-FontAwesome-$(PYTHON_FLASK_FONTAWESOME_VERSION).tar.gz
PYTHON_FLASK_FONTAWESOME_SITE = https://files.pythonhosted.org/packages/87/40/d5780675fa8bec026a26cafcb4e9f31eec60d878896dee42ee7cda8f35cd
PYTHON_FLASK_FONTAWESOME_SETUP_TYPE = setuptools
PYTHON_FLASK_FONTAWESOME_LICENSE = Apache-2.0, MIT

$(eval $(python-package))
