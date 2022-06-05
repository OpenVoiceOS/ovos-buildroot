################################################################################
#
# python-neon-solver-plugin-wikipedia
#
################################################################################

PYTHON_NEON_SOLVER_PLUGIN_WIKIPEDIA_VERSION = f675e025160259eb659a210c68782e66d1f78f99
PYTHON_NEON_SOLVER_PLUGIN_WIKIPEDIA_SITE = $(call github,NeonGeckoCom,neon-solver-plugin-wikipedia,$(PYTHON_NEON_SOLVER_PLUGIN_WIKIPEDIA_VERSION))
PYTHON_NEON_SOLVER_PLUGIN_WIKIPEDIA_SETUP_TYPE = setuptools
PYTHON_NEON_SOLVER_PLUGIN_WIKIPEDIA_LICENSE_FILES = LICENSE

$(eval $(python-package))
