################################################################################
#
# python-google-auth
#
################################################################################

PYTHON_GOOGLE_AUTH_VERSION = 1.5.1
PYTHON_GOOGLE_AUTH_SOURCE = google-auth-$(PYTHON_GOOGLE_AUTH_VERSION).tar.gz
PYTHON_GOOGLE_AUTH_SITE = https://files.pythonhosted.org/packages/7e/cd/dae5c39974b040741215ed346263152c93af21a22dc124c7ad451fbee417
PYTHON_GOOGLE_AUTH_SETUP_TYPE = setuptools
PYTHON_GOOGLE_AUTH_LICENSE = Apache-2.0
PYTHON_GOOGLE_AUTH_LICENSE_FILES = LICENSE

$(eval $(python-package))
