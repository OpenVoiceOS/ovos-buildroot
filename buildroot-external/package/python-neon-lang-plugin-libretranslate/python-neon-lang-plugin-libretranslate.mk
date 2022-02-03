################################################################################
#
# python-neon-lang-plugin-libretranslate.mk
#
################################################################################

PYTHON_NEON_LANG_PLUGIN_LIBRETRANSLATE_VERSION = c071ea344c1fa9f2368c52d88ac0e2f3d64b938a
PYTHON_NEON_LANG_PLUGIN_LIBRETRANSLATE_SITE = $(call github,NeonGeckoCom,neon-lang-plugin-libretranslate,$(PYTHON_NEON_LANG_PLUGIN_LIBRETRANSLATE_VERSION))
PYTHON_NEON_LANG_PLUGIN_LIBRETRANSLATE_SETUP_TYPE = setuptools
PYTHON_NEON_LANG_PLUGIN_LIBRETRANSLATE_LICENSE_FILES = LICENSE

$(eval $(python-package))
