################################################################################
#
# hostname-service
#
################################################################################

HOSTNAME_SERVICE_VERSION = 0.1.0
HOSTNAME_SERVICE_SITE = $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/hostname-service
HOSTNAME_SERVICE_SITE_METHOD = local
HOSTNAME_SERVICE_LICENSE = Apache License 2.0
HOSTNAME_SERVICE_LICENSE_FILES = LICENSE

define HOSTNAME_SERVICE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 644 $(@D)/hostname.service \
		$(TARGET_DIR)/usr/lib/systemd/system/hostname.service
endef

$(eval $(generic-package))
