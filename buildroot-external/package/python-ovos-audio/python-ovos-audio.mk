################################################################################
#
# python-ovos-audio
#
################################################################################

PYTHON_OVOS_AUDIO_VERSION = 3903c8cbb0072fc03a260020b5ef4e6e6b823377
PYTHON_OVOS_AUDIO_SITE = $(call github,OpenVoiceOS,ovos-audio,$(PYTHON_OVOS_AUDIO_VERSION))
PYTHON_OVOS_AUDIO_SETUP_TYPE = setuptools
PYTHON_OVOS_AUDIO_LICENSE_FILES = LICENSE
PYTHON_OVOS_AUDIO_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
