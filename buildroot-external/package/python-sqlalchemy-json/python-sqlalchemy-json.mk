################################################################################
#
# python-sqlalchemy-json
#
################################################################################

PYTHON_SQLALCHEMY_JSON_VERSION = 0.5.0
PYTHON_SQLALCHEMY_JSON_SOURCE = sqlalchemy-json-$(PYTHON_SQLALCHEMY_JSON_VERSION).tar.gz
PYTHON_SQLALCHEMY_JSON_SITE = https://files.pythonhosted.org/packages/8e/cc/9fcde4f5739de1499179dde18d1734f42d1bb5bc9c7188e582d96b53ebeb
PYTHON_SQLALCHEMY_JSON_SETUP_TYPE = setuptools

$(eval $(python-package))
