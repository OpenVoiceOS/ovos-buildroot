################################################################################
#
# python-json-database
#
################################################################################

PYTHON_JSON_DATABASE_VERSION = 0.5.6
PYTHON_JSON_DATABASE_SOURCE = json_database-$(PYTHON_JSON_DATABASE_VERSION).tar.gz
PYTHON_JSON_DATABASE_SITE = https://files.pythonhosted.org/packages/b1/2b/545bb5cafe2cd3876475669c12f31bb1076b609177f16d6efaeb214d038c
PYTHON_JSON_DATABASE_SETUP_TYPE = setuptools

$(eval $(python-package))
