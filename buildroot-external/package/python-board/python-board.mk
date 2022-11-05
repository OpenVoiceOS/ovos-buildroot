################################################################################
#
# python-board
#
################################################################################

PYTHON_BOARD_VERSION = 1.0
PYTHON_BOARD_SOURCE = board-$(PYTHON_BOARD_VERSION).tar.gz
PYTHON_BOARD_SITE = https://files.pythonhosted.org/packages/de/7d/4de4e7b0eb780854e2c1258225a831ef29c447f0e934347ce58128939b69
PYTHON_BOARD_SETUP_TYPE = setuptools
PYTHON_BOARD_LICENSE = unlicensed

$(eval $(python-package))
