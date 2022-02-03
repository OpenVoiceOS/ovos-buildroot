################################################################################
#
# python-neon-solver-plugin-ddg
#
################################################################################

PYTHON_NEON_SOLVER_PLUGIN_DDG_VERSION = 0afd34a5c11dff119576707b3885f054adb9db91
PYTHON_NEON_SOLVER_PLUGIN_DDG_SITE = $(call github,NeonGeckoCom,neon-solver-plugin-ddg,$(PYTHON_NEON_SOLVER_PLUGIN_DDG_VERSION))
PYTHON_NEON_SOLVER_PLUGIN_DDG_SETUP_TYPE = setuptools
PYTHON_NEON_SOLVER_PLUGIN_DDG_LICENSE_FILES = LICENSE

$(eval $(python-package))
