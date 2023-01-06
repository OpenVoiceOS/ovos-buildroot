################################################################################
#
# skill-ovos-filebrowser
#
################################################################################

SKILL_OVOS_FILEBROWSER_VERSION = bf889e80e7fcbdbb2fd501de3610420491412b86
SKILL_OVOS_FILEBROWSER_SITE = $(call github,OpenVoiceOS,skill-ovos-filebrowser,$(SKILL_OVOS_FILEBROWSER_VERSION))
SKILL_OVOS_FILEBROWSER_SETUP_TYPE = setuptools
SKILL_OVOS_FILEBROWSER_LICENSE_FILES = LICENSE

$(eval $(python-package))
