################################################################################
#
# pa-volume
#
################################################################################

PA_VOLUME_VERSION = cfbff58992f6ca091c4c5784a6eb25bc422d7ae8
PA_VOLUME_SITE = $(call github,rhaas80,pa_volume,$(PA_VOLUME_VERSION))

define PA_VOLUME_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) all
endef

define PA_VOLUME_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/pa_volume \
		$(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
