################################################################################
#
# python-neon-solvers
#
################################################################################

PYTHON_NEON_SOLVERS_VERSION = b593b8ae9a7e7eae3b515940fa671d6a03956555
PYTHON_NEON_SOLVERS_SITE = $(call github,NeonGeckoCom,neon_solvers,$(PYTHON_NEON_SOLVERS_VERSION))
PYTHON_NEON_SOLVERS_SETUP_TYPE = setuptools
PYTHON_NEON_SOLVERS_LICENSE_FILES = LICENSE

$(eval $(python-package))
