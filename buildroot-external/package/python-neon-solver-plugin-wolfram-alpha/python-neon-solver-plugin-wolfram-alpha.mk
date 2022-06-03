################################################################################
#
# python-neon-solver-plugin-wolfram-alpha
#
################################################################################

PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_VERSION = 36ab1c27bab47e3fff9bb0bed88aa498ce7f19ff
PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_SITE = $(call github,NeonGeckoCom,neon-solver-plugin-wolfram_alpha,$(PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_VERSION))
PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_SETUP_TYPE = setuptools
PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_LICENSE_FILES = LICENSE

$(eval $(python-package))
