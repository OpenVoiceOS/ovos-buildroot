################################################################################
#
# python-fasteners
#
################################################################################

PYTHON_FASTENERS_VERSION = 0.14.1
PYTHON_FASTENERS_SOURCE = fasteners-$(PYTHON_FASTENERS_VERSION).tar.gz
PYTHON_FASTENERS_SITE = https://files.pythonhosted.org/packages/f4/6f/41b835c9bf69b03615630f8a6f6d45dafbec95eb4e2bb816638f043552b2
PYTHON_FASTENERS_SETUP_TYPE = setuptools
PYTHON_FASTENERS_LICENSE = Apache-2.0
PYTHON_FASTENERS_LICENSE_FILES = LICENSE

$(eval $(python-package))
