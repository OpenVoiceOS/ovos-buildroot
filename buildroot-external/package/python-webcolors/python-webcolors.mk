################################################################################
#
# python-webcolors
#
################################################################################

PYTHON_WEBCOLORS_VERSION = 1.13
PYTHON_WEBCOLORS_SOURCE = webcolors-$(PYTHON_WEBCOLORS_VERSION).tar.gz
PYTHON_WEBCOLORS_SITE = https://files.pythonhosted.org/packages/a1/fb/f95560c6a5d4469d9c49e24cf1b5d4d21ffab5608251c6020a965fb7791c
PYTHON_WEBCOLORS_SETUP_TYPE = setuptools

$(eval $(python-package))
