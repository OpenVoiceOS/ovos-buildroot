################################################################################
#
# virtual-touch
#
################################################################################

VIRTUAL_TOUCH_VERSION = 913a36c83fc1ebf4396fec19a94b2092ebee6d4c
VIRTUAL_TOUCH_SITE = $(call github,vi,virtual_touchscreen,$(VIRTUAL_TOUCH_VERSION))

$(eval $(kernel-module))

define VIRTUAL_TOUCH_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/virtual-touch/virtual-touch.conf \
		$(TARGET_DIR)/etc/modules-load.d/virtual-touch.conf
endef

$(eval $(generic-package))
