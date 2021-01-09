################################################################################
#
# python-flask-mail
#
################################################################################

PYTHON_FLASK_MAIL_VERSION = 0.9.1
PYTHON_FLASK_MAIL_SOURCE = Flask-Mail-$(PYTHON_FLASK_MAIL_VERSION).tar.gz
PYTHON_FLASK_MAIL_SITE = https://files.pythonhosted.org/packages/05/2f/6a545452040c2556559779db87148d2a85e78a26f90326647b51dc5e81e9
PYTHON_FLASK_MAIL_SETUP_TYPE = setuptools
PYTHON_FLASK_MAIL_LICENSE = FIXME: license id couldn't be detected, BSD-3-Clause
PYTHON_FLASK_MAIL_LICENSE_FILES = LICENSE docs/_themes/LICENSE

$(eval $(python-package))
