################################################################################
#
# python-neon-solver-plugin-ddg
#
################################################################################

PYTHON_NEON_SOLVER_PLUGIN_DDG_VERSION = 80c9ce0cc6abb78ff5e7613434a710d720eff899
PYTHON_NEON_SOLVER_PLUGIN_DDG_SITE = $(call github,NeonGeckoCom,neon-solver-plugin-ddg,$(PYTHON_NEON_SOLVER_PLUGIN_DDG_VERSION))
PYTHON_NEON_SOLVER_PLUGIN_DDG_SETUP_TYPE = setuptools
PYTHON_NEON_SOLVER_PLUGIN_DDG_LICENSE_FILES = LICENSE

$(eval $(python-package))
