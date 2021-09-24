################################################################################
#
# python-audio-metadata
#
################################################################################

PYTHON_AUDIO_METADATA_VERSION = 0.11.1
PYTHON_AUDIO_METADATA_SOURCE = audio-metadata-$(PYTHON_AUDIO_METADATA_VERSION).tar.gz
PYTHON_AUDIO_METADATA_SITE = https://files.pythonhosted.org/packages/29/a3/3e6657b60b31199ff74827e92d807e83e628503c3bc27d34186bb5306e6f
PYTHON_AUDIO_METADATA_SETUP_TYPE = setuptools
PYTHON_AUDIO_METADATA_LICENSE = MIT
PYTHON_AUDIO_METADATA_LICENSE_FILES = LICENSE

$(eval $(python-package))
