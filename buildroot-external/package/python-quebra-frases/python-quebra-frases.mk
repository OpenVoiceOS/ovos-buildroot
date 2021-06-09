################################################################################
#
# python-quebra-frases
#
################################################################################

PYTHON_QUEBRA_FRASES_VERSION = 0.3.7
PYTHON_QUEBRA_FRASES_SOURCE = quebra_frases-$(PYTHON_QUEBRA_FRASES_VERSION).tar.gz
PYTHON_QUEBRA_FRASES_SITE = https://files.pythonhosted.org/packages/04/8f/dcc0beeb6e164f44e03d1501b70733a1d7f069c9d59354911537d84b71e6
PYTHON_QUEBRA_FRASES_SETUP_TYPE = setuptools
PYTHON_QUEBRA_FRASES_LICENSE = apache-2.0
PYTHON_QUEBRA_FRASES_LICENSE_FILES = LICENSE

$(eval $(python-package))
