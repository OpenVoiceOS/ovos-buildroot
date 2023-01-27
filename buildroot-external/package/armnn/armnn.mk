################################################################################
#
# armnn
#
################################################################################

ARMNN_VERSION = v22.11.01
ARMNN_SITE = $(call github,ARM-software,armnn,$(ARMNN_VERSION))
ARMNN_LICENSE = MIT

ARMNN_INSTALL_STAGING = YES
ARMNN_DEPENDENCIES = host-pkgconf compute-library tensorflow-lite
ARMNN_SUPPORTS_IN_SOURCE_BUILD = NO

ARMNN_CONF_OPTS = \
	-DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -fPIC -Wno-error=missing-field-initializers" \
	-DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -fPIC -Wno-error=missing-field-initializers" \
	-DCMAKE_SHARED_LINKER_FLAGS="$(TARGET_LDFLAGS) -fPIC -Wno-error=missing-field-initializers" \
	-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
	-DBUILD_SHARED_LIBS=ON \
	-DBUILD_TF_LITE_PARSER=0 \
	-DBUILD_ARMNN_TFLITE_DELEGATE=ON \
	-DARMCOMPUTENEON=ON \
	-DARMCOMPUTECL=0 \
	-DARMNNREF=0 \
	-DARMCOMPUTE_ROOT="$(BUILD_DIR)/compute-library-$(COMPUTE_LIBRARY_VERSION)" \
	-DARMCOMPUTE_BUILD_DIR="$(BUILD_DIR)/compute-library-$(COMPUTE_LIBRARY_VERSION)/buildroot-build" \
	-DTENSORFLOW_ROOT="$(BUILD_DIR)/tensorflow-lite-$(TENSORFLOW_LITE_VERSION)" \
	-DTF_LITE_SCHEMA_INCLUDE_PATH="$(BUILD_DIR)/tensorflow-lite-$(TENSORFLOW_LITE_VERSION)/tensorflow/lite/schema" \
	-DTFLITE_LIB_ROOT="$(STAGING_DIR)/usr/lib" \
	-DTfLite_Schema_INCLUDE_PATH="$(BUILD_DIR)/tensorflow-lite-$(TENSORFLOW_LITE_VERSION)/tensorflow/lite/schema" \
	-DTfLite_LIB="$(STAGING_DIR)/usr/lib/libtensorflow-lite.so"

$(eval $(cmake-package))
