################################################################################
#
# python-json-database
#
################################################################################

PYTHON_JSON_DATABASE_VERSION = 0.5.2
PYTHON_JSON_DATABASE_SOURCE = json_database-$(PYTHON_JSON_DATABASE_VERSION).tar.gz
PYTHON_JSON_DATABASE_SITE = https://files.pythonhosted.org/packages/e1/f0/3a50ed9deed6b55697e30d874605900a5694e8653b9d9747597b1a670dee
PYTHON_JSON_DATABASE_SETUP_TYPE = setuptools

$(eval $(python-package))
