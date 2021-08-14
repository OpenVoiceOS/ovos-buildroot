################################################################################
#
# python-ovos-workshop
#
################################################################################

PYTHON_OVOS_WORKSHOP_VERSION = c06ad1394e996c1007c3802c7d836b776dbf75be
PYTHON_OVOS_WORKSHOP_SITE = $(call github,OpenVoiceOS,OVOS-workshop,$(PYTHON_OVOS_WORKSHOP_VERSION))
PYTHON_OVOS_WORKSHOP_SETUP_TYPE = setuptools
PYTHON_OVOS_WORKSHOP_LICENSE_FILES = LICENSE

$(eval $(python-package))
