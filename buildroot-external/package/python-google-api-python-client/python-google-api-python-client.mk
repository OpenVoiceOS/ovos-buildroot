################################################################################
#
# python-google-api-python-client
#
################################################################################

PYTHON_GOOGLE_API_PYTHON_CLIENT_VERSION = 1.6.4
PYTHON_GOOGLE_API_PYTHON_CLIENT_SOURCE = google-api-python-client-$(PYTHON_GOOGLE_API_PYTHON_CLIENT_VERSION).tar.gz
PYTHON_GOOGLE_API_PYTHON_CLIENT_SITE = https://files.pythonhosted.org/packages/b4/b3/f9be3f2ec31491c8f74e5c7905fabe890dedb4e1e8db5c951df3c167be41
PYTHON_GOOGLE_API_PYTHON_CLIENT_SETUP_TYPE = setuptools
PYTHON_GOOGLE_API_PYTHON_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
