################################################################################
#
# python-google-auth-httplib2
#
################################################################################

PYTHON_GOOGLE_AUTH_HTTPLIB2_VERSION = 0.0.3
PYTHON_GOOGLE_AUTH_HTTPLIB2_SOURCE = google-auth-httplib2-$(PYTHON_GOOGLE_AUTH_HTTPLIB2_VERSION).tar.gz
PYTHON_GOOGLE_AUTH_HTTPLIB2_SITE = https://files.pythonhosted.org/packages/e7/32/ac7f30b742276b4911a1439c5291abab1b797ccfd30bc923c5ad67892b13
PYTHON_GOOGLE_AUTH_HTTPLIB2_SETUP_TYPE = setuptools
PYTHON_GOOGLE_AUTH_HTTPLIB2_LICENSE = Apache-2.0
PYTHON_GOOGLE_AUTH_HTTPLIB2_LICENSE_FILES = LICENSE

$(eval $(python-package))
