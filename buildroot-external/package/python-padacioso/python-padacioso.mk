################################################################################
#
# python-padacioso
#
################################################################################

PYTHON_PADACIOSO_VERSION = 0.1.1
PYTHON_PADACIOSO_SOURCE = padacioso-$(PYTHON_PADACIOSO_VERSION).tar.gz
PYTHON_PADACIOSO_SITE = https://files.pythonhosted.org/packages/7f/3d/292f14feaa17d724561d030616920e4dc4163aab13fd4e88d3071c1023a5
PYTHON_PADACIOSO_SETUP_TYPE = setuptools
PYTHON_PADACIOSO_LICENSE = apache-2.0

$(eval $(python-package))
