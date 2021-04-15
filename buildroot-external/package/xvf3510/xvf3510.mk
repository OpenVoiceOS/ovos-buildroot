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
		$(TARGET_DIR)/usr/sbin
	$(INSTALL) -D -m 0755 $(@D)/resources/clk_dac_setup/setup_mclk \
		$(TARGET_DIR)/usr/sbin

	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/xvf3510/xvf3510.service \
		$(TARGET_DIR)/usr/lib/systemd/system/xvf3510.service

	$(INSTALL) -D -m 755 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/xvf3510/xvf3510-start \
                $(TARGET_DIR)/usr/sbin/xvf3510-start
	$(INSTALL) -D -m 755 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/xvf3510/xvf3510-stop \
                $(TARGET_DIR)/usr/sbin/xvf3510-stop
	$(INSTALL) -D -m 755 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/xvf3510/xvf3510-flash \
                $(TARGET_DIR)/usr/sbin/xvf3510-flash

	mkdir -p $(TARGET_DIR)/usr/lib/firmware/xvf3510
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/xvf3510/app_xvf3510_int_spi_boot_v4_1_0.bin \
                $(TARGET_DIR)/usr/lib/firmware/xvf3510/app_xvf3510_int_spi_boot_v4_1_0.bin
endef

$(eval $(generic-package))
