################################################################################
#
# alsa-ucm-conf
#
################################################################################

ALSA_UCM_CONF_VERSION = 1.2.12
ALSA_UCM_CONF_SITE = $(call github,alsa-project,alsa-ucm-conf,v$(ALSA_UCM_CONF_VERSION))
ALSA_UCM_CONF_DEPENDENCIES = alsa-lib

define ALSA_UCM_CONF_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/alsa
	cp -dpfr $(@D)/ucm $(TARGET_DIR)/usr/share/alsa/
	cp -dpfr $(@D)/ucm2 $(TARGET_DIR)/usr/share/alsa/
endef

$(eval $(generic-package))
