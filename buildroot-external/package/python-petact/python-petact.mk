################################################################################
#
# python-petact
#
################################################################################

PYTHON_PETACT_VERSION = 0.1.2
PYTHON_PETACT_SOURCE = petact-$(PYTHON_PETACT_VERSION).tar.gz
PYTHON_PETACT_SITE = https://files.pythonhosted.org/packages/5f/89/62b285704ac9823ade8178a1a4c8bcd3529871de3c162084b8dde6d0d6ff
PYTHON_PETACT_SETUP_TYPE = setuptools

$(eval $(python-package))
