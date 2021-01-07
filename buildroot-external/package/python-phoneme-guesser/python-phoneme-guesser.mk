################################################################################
#
# python-phoneme-guesser
#
################################################################################

PYTHON_PHONEME_GUESSER_VERSION = 0.1.0
PYTHON_PHONEME_GUESSER_SOURCE = phoneme_guesser-$(PYTHON_PHONEME_GUESSER_VERSION).tar.gz
PYTHON_PHONEME_GUESSER_SITE = https://files.pythonhosted.org/packages/c7/ea/c5b389b6d593212935412e5f314978d860bc59c393a8c1029ada3992f4bd
PYTHON_PHONEME_GUESSER_SETUP_TYPE = setuptools

$(eval $(python-package))
