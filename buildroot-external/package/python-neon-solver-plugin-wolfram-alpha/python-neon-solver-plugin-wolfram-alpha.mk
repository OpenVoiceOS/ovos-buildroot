################################################################################
#
# python-neon-solver-plugin-wolfram-alpha
#
################################################################################

PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_VERSION = 10f163f23bda9a123c89c11dfbcdf3ae804569f1
PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_SITE = $(call github,NeonGeckoCom,neon-solver-plugin-wolfram_alpha,$(PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_VERSION))
PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_SETUP_TYPE = setuptools
PYTHON_NEON_SOLVER_PLUGIN_WOLFRAM_ALPHA_LICENSE_FILES = LICENSE

$(eval $(python-package))
