################################################################################
#
# python-google-trans-new
#
################################################################################

PYTHON_GOOGLE_TRANS_NEW_VERSION = 1.1.9
PYTHON_GOOGLE_TRANS_NEW_SOURCE = google_trans_new-$(PYTHON_GOOGLE_TRANS_NEW_VERSION).tar.gz
PYTHON_GOOGLE_TRANS_NEW_SITE = https://files.pythonhosted.org/packages/4e/37/c4b72558b6b645bee86557479677c97e4161cb13fc3cc6ac55f872782559
PYTHON_GOOGLE_TRANS_NEW_SETUP_TYPE = setuptools
PYTHON_GOOGLE_TRANS_NEW_LICENSE = MIT

$(eval $(python-package))
