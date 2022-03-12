################################################################################
#
# python-json-database
#
################################################################################

PYTHON_JSON_DATABASE_VERSION = 0.7.0
PYTHON_JSON_DATABASE_SOURCE = json_database-$(PYTHON_JSON_DATABASE_VERSION).tar.gz
PYTHON_JSON_DATABASE_SITE = https://files.pythonhosted.org/packages/ef/dc/6d6a6e4d4ab02dcd08a83344818c943799eb68b79619ff862e54c64a2c56
PYTHON_JSON_DATABASE_SETUP_TYPE = setuptools

$(eval $(python-package))
