################################################################################
#
# python-neon-solvers
#
################################################################################

PYTHON_NEON_SOLVERS_VERSION = c37161405cd6aa583e5623315342986cf5c829af
PYTHON_NEON_SOLVERS_SITE = $(call github,NeonGeckoCom,neon_solvers,$(PYTHON_NEON_SOLVERS_VERSION))
PYTHON_NEON_SOLVERS_SETUP_TYPE = setuptools
PYTHON_NEON_SOLVERS_LICENSE_FILES = LICENSE

$(eval $(python-package))
