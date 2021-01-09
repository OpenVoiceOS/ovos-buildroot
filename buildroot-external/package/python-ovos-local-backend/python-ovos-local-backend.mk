################################################################################
#
# python-ovos-local-backend
#
################################################################################

PYTHON_OVOS_LOCAL_BACKEND_VERSION = 0.1.0
PYTHON_OVOS_LOCAL_BACKEND_SOURCE = ovos-local-backend-$(PYTHON_OVOS_LOCAL_BACKEND_VERSION).tar.gz
PYTHON_OVOS_LOCAL_BACKEND_SITE = https://files.pythonhosted.org/packages/b6/b9/18c2f9961fa4baa5afaac0387ec85bc1ae6fef82bbeac335c4c6b9c8ec10
PYTHON_OVOS_LOCAL_BACKEND_SETUP_TYPE = setuptools

$(eval $(python-package))
