################################################################################
#
# python-neon-utterance-plgin-rake
#
################################################################################

PYTHON_NEON_UTTERANCE_PLUGIN_RAKE_VERSION = 62df5b1a1d88336dafce903022896ef53521784f
PYTHON_NEON_UTTERANCE_PLUGIN_RAKE_SITE = $(call github,NeonGeckoCom,neon-utterance-plugin-RAKE,$(PYTHON_NEON_UTTERANCE_PLUGIN_RAKE_VERSION))
PYTHON_NEON_UTTERANCE_PLUGIN_RAKE_SETUP_TYPE = setuptools
PYTHON_NEON_UTTERANCE_PLUGIN_RAKE_LICENSE_FILES = LICENSE

$(eval $(python-package))
