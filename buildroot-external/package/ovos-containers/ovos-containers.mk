################################################################################
#
# OVOS Container images
#
################################################################################

OVOS_CONTAINERS_VERSION = 1.0.0
OVOS_CONTAINERS_LICENSE = Apache License 2.0
OVOS_CONTAINERS_LICENSE_FILES = $(BR2_EXTERNAL_OPENVOICEOS_PATH)/../LICENSE
OVOS_CONTAINERS_SITE = $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-containers
OVOS_CONTAINERS_SITE_METHOD = local
#OVOS_CONTAINERS_DEPENDENCIES = host-skopeo host-podman host-jq

OVOS_CONTAINERS_IMAGES = ovos-messagebus \
			 ovos-phal \
			 ovos-listener \
			 ovos-audio \
			 ovos-core-buildroot \
			 ovos-gui-websocket \
			 ovos-cli

ifeq ($(BR2_PACKAGE_OVOS_CONTAINERS_GUI),y)
OVOS_CONTAINERS_IMAGES += ovos-gui-shell
endif

define OVOS_CONTAINERS_BUILD_CMDS
	$(Q)mkdir -p $(@D)/images
	$(Q)mkdir -p $(OVOS_CONTAINERS_DL_DIR)/$(BR2_PACKAGE_OVOS_CONTAINERS_ARCH)
	$(foreach image,$(OVOS_CONTAINERS_IMAGES),\
		$(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-containers/fetch-container-image.sh \
			$(BR2_PACKAGE_OVOS_CONTAINERS_ARCH) $(image) "$(OVOS_CONTAINERS_DL_DIR)/$(BR2_PACKAGE_OVOS_CONTAINERS_ARCH)" "$(@D)/images"
	)
endef

OVOS_CONTAINERS_INSTALL_IMAGES = YES

define OVOS_CONTAINERS_INSTALL_IMAGES_CMDS
	$(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-containers/install-container-image.sh "$(@D)" "$(TARGET_DIR)/home/ovos/.local/share/containers/storage"
	rm -rf $(TARGET_DIR)/home/ovos/.local/share/containers/storage/storage.lock
	rm -rf $(TARGET_DIR)/home/ovos/.local/share/containers/storage/userns.lock
	rm -rf $(TARGET_DIR)/home/ovos/.local/share/containers/storage/libpod
endef

$(eval $(generic-package))
