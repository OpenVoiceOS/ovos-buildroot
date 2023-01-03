################################################################################
#
# hdf5
#
################################################################################

HDF5_VERSION = hdf5-1_12_2
HDF5_SITE = $(call github,HDFGroup,hdf5,$(HDF5_VERSION))
HDF5_SUPPORTS_IN_SOURCE_BUILD = NO

HDF5_INSTALL_STAGING = YES
HDF5_PRE_CONFIGURE_HOOKS = HDF5_INIT

HDF5_CONF_OPTS += \
	-DTEST_LFS_WORKS_RUN=0 \
	-DTEST_LFS_WORKS_RUN__TRYRUN_OUTPUT="" \
	-DH5_PRINTF_LL_TEST_RUN=0 \
	-DH5_PRINTF_LL_TEST_RUN__TRYRUN_OUTPUT="H5_PRINTF_LL_WIDTH=[l]" \
	-DRUN_RESULT_VAR=0 \
	-DRUN_RESULT_VAR__TRYRUN_OUTPUT="" \
	-DH5_LDOUBLE_TO_LONG_SPECIAL_RUN=1 \
	-DH5_LDOUBLE_TO_LONG_SPECIAL_RUN__TRYRUN_OUTPUT="" \
	-DH5_LONG_TO_LDOUBLE_SPECIAL_RUN=1 \
	-DH5_LONG_TO_LDOUBLE_SPECIAL_RUN__TRYRUN_OUTPUT="" \
	-DH5_LDOUBLE_TO_LLONG_ACCURATE_RUN=0 \
	-DH5_LDOUBLE_TO_LLONG_ACCURATE_RUN__TRYRUN_OUTPUT="" \
	-DH5_LLONG_TO_LDOUBLE_CORRECT_RUN=0 \
	-DH5_LLONG_TO_LDOUBLE_CORRECT_RUN__TRYRUN_OUTPUT="" \
	-DH5_NO_ALIGNMENT_RESTRICTIONS_RUN=0 \
	-DH5_NO_ALIGNMENT_RESTRICTIONS_RUN__TRYRUN_OUTPUT="" \
	-DH5_DISABLE_SOME_LDOUBLE_CONV_RUN=1 \
	-DH5_DISABLE_SOME_LDOUBLE_CONV_RUN__TRYRUN_OUTPUT="" \
	-DHDF5_BUILD_CPP_LIB=ON \
	-DHDF5_ENABLE_Z_LIB_SUPPORT=ON

define HDF5_INIT
	mkdir -p $(@D)/src/shared
	$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/hdf5/*.c \
		$(@D)/src/
	$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/hdf5/*.c \
		$(@D)/src/shared/

	 mkdir -p $(@D)/buildroot-build/src/shared
        $(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/hdf5/*.c \
                $(@D)/buildroot-build/src/
        $(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/hdf5/*.c \
                $(@D)/buildroot-build/src/shared/
	touch $(@D)/src/gen_SRCS.stamp1
	touch $(@D)/src/gen_SRCS.stamp2
	touch $(@D)/src/shared/shared_gen_SRCS.stamp1
        touch $(@D)/src/shared/shared_gen_SRCS.stamp2
	touch $(@D)/buildroot-build/src/gen_SRCS.stamp1
        touch $(@D)/buildroot-build/src/gen_SRCS.stamp2
        touch $(@D)/buildroot-build/src/shared/shared_gen_SRCS.stamp1
        touch $(@D)/buildroot-build/src/shared/shared_gen_SRCS.stamp2
endef

$(eval $(cmake-package))
