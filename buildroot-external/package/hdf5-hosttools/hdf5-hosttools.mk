################################################################################
#
# hdf5
#
################################################################################

HDF5_VERSION = cfd5059e77e2e411a94a13d2fb033224736be09d
HDF5_SITE = $(call github,HDFGroup,hdf5,$(HDF5_VERSION))
HDF5_SUPPORTS_IN_SOURCE_BUILD = NO

HDF5_INSTALL_STAGING = YES
HDF5_DEPENDENCIES = host-hdf5

HDF5_CONF_OPTS += \
	-DHDF5_BUILD_CPP_LIB=ON \
	-DHDF5_ENABLE_Z_LIB_SUPPORT=ON \
	-C$(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/hdf5/TryRunResults_out.cmake

$(eval $(cmake-package))

HDF5_POST_INSTALL_HOOKS = HDF5_HOST_BIN

define HDF5_HOST_BIN
	$(INSTALL) -D -m 755 $(@D)/buildroot-build/bin/H5detect \
		$(HOST_DIR)/bin/H5detect

	$(INSTALL) -D -m 755 $(@D)/buildroot-build/bin/H5make_libsettings \
                $(HOST_DIR)/bin/H5make_libsettings
endef

$(eval $(host-cmake-package))
