################################################################################
#
# python-neon-transformers
#
################################################################################

PYTHON_NEON_TRANSFORMERS_VERSION = 916c55f86f5ef5db82f6e53f50945a037faeaf2b
PYTHON_NEON_TRANSFORMERS_SITE = $(call github,NeonGeckoCom,neon-transformers,$(PYTHON_NEON_TRANSFORMERS_VERSION))
PYTHON_NEON_TRANSFORMERS_SETUP_TYPE = setuptools
PYTHON_NEON_TRANSFORMERS_LICENSE_FILES = LICENSE

$(eval $(python-package))
