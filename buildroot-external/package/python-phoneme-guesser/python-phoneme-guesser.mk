################################################################################
#
# python-phoneme-guesser
#
################################################################################

PYTHON_PHONEME_GUESSER_VERSION = 0.1.1
PYTHON_PHONEME_GUESSER_SOURCE = phoneme_guesser-$(PYTHON_PHONEME_GUESSER_VERSION).tar.gz
PYTHON_PHONEME_GUESSER_SITE = https://files.pythonhosted.org/packages/bc/a8/1a341ca70837374a954d46a616eed073465938728f96b325c87d73ce54fc
PYTHON_PHONEME_GUESSER_SETUP_TYPE = setuptools

$(eval $(python-package))
