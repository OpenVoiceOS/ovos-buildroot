################################################################################
#
# xvf3510
#
################################################################################

XVF3510_VERSION = 4cfcc2c418ac0076277b11aa9e410816a62ce673
XVF3510_SITE = $(call github,xmos,vocalfusion-rpi-setup,$(XVF3510_VERSION))
XVF3510_MODULE_SUBDIRS = loader/i2s_master
XVF3510_MODULE_MAKE_OPTS = CFLAGS_MODULE="-DRPI_4B -DI2S_MASTER" \
	KVER=$(LINUX_VERSION_PROBED) \
	KSRC=$(LINUX_DIR)

XVF3510_POST_EXTRACT_HOOKS = XVF3510_MOVE_SRC_FILE

define XVF3510_MOVE_SRC_FILE
	cp $(@D)/loader/src/loader.c $(@D)/loader/i2s_master/i2s_master_loader.c
endef

$(eval $(kernel-module))

define XVF3510_BUILD_CMDS
	$(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/resources/clk_dac_setup default
endef

define XVF3510_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/resources/clk_dac_setup/setup_bclk \
		$(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0755 $(@D)/resources/clk_dac_setup/setup_mclk \
		$(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
