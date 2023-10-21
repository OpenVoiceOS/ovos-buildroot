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

OVOS_CONTAINERS_IMAGES = $(call qstrip,$(BR2_PACKAGE_OVOS_CONTAINERS))

define OVOS_CONTAINERS_BUILD_CMDS
	$(Q)mkdir -p $(@D)/images
	$(Q)mkdir -p $(OVOS_CONTAINERS_DL_DIR)
	$(foreach image,$(OVOS_CONTAINERS_IMAGES),\
		$(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-containers/fetch-container-image.sh \
			$(BR2_PACKAGE_OVOS_CONTAINERS_ARCH) $(image) "$(OVOS_CONTAINERS_DL_DIR)" "$(@D)/images"
	)
endef

$(eval $(generic-package))
