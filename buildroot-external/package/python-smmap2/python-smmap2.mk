################################################################################
#
# python-smmap2
#
################################################################################

PYTHON_SMMAP2_VERSION = 2.0.4
PYTHON_SMMAP2_SOURCE = smmap2-$(PYTHON_SMMAP2_VERSION).tar.gz
PYTHON_SMMAP2_SITE = https://files.pythonhosted.org/packages/ad/e9/0fb974b182ff41d28ad267d0b4201b35159619eb610ea9a2e036817cb0b8
PYTHON_SMMAP2_SETUP_TYPE = setuptools
PYTHON_SMMAP2_LICENSE = BSD-3-Clause
PYTHON_SMMAP2_LICENSE_FILES = LICENSE

$(eval $(python-package))
