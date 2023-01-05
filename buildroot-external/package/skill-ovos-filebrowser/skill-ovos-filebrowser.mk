################################################################################
#
# skill-ovos-filebrowser
#
################################################################################

SKILL_OVOS_FILEBROWSER_VERSION = 5e07ca15c67d5e8f07c2a03606a44e8e2808db85
SKILL_OVOS_FILEBROWSER_SITE = $(call github,OpenVoiceOS,skill-ovos-filebrowser,$(SKILL_OVOS_FILEBROWSER_VERSION))
SKILL_OVOS_FILEBROWSER_SETUP_TYPE = setuptools
SKILL_OVOS_FILEBROWSER_LICENSE_FILES = LICENSE

$(eval $(python-package))
