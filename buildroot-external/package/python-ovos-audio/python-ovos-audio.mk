################################################################################
#
# python-ovos-audio
#
################################################################################

PYTHON_OVOS_AUDIO_VERSION = 3805078c09e46e8827e4eab93e1c943e5599a3e4
PYTHON_OVOS_AUDIO_SITE = $(call github,OpenVoiceOS,ovos-audio,$(PYTHON_OVOS_AUDIO_VERSION))
PYTHON_OVOS_AUDIO_SETUP_TYPE = setuptools
PYTHON_OVOS_AUDIO_LICENSE_FILES = LICENSE
PYTHON_OVOS_AUDIO_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
