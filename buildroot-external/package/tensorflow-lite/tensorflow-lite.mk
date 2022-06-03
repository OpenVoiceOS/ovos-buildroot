################################################################################
#
# tensorflow-lite
#
################################################################################

TENSORFLOW_LITE_VERSION = v2.9.1
TENSORFLOW_LITE_SITE = $(call github,tensorflow,tensorflow,$(TENSORFLOW_LITE_VERSION))
TENSORFLOW_LITE_SUBDIR = tensorflow/lite
TENSORFLOW_LITE_LICENSE = Apache License 2.0

TENSORFLOW_LITE_INSTALL_STAGING = YES

TENSORFLOW_LITE_DEPENDENCIES = host-pkgconf
TENSORFLOW_LITE_SUPPORTS_IN_SOURCE_BUILD = NO

#TENSORFLOW_LITE_CONF_OPTS += CFLAGS="$(TARGET_CFLAGS) -funsafe-math-optimizations
#TENSORFLOW_LITE_CONF_OPTS += CXXFLAGS="$(TARGET_CFLAGS) -funsafe-math-optimizations

TENSORFLOW_LITE_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -funsafe-math-optimizations \
				-I$(STAGING_DIR)/usr/include/python$(PYTHON3_VERSION_MAJOR) \
				-I$(STAGING_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/numpy/core/include \
				-I$(STAGING_DIR)/usr/include/pybind11" \
			     -DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) -funsafe-math-optimizations \
				-I$(STAGING_DIR)/usr/include/python$(PYTHON3_VERSION_MAJOR) \
				-I$(STAGING_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/numpy/core/include \
				-I$(STAGING_DIR)/usr/include/pybind11" \
			     -DCMAKE_SYSTEM_NAME=Linux \
			     -DCMAKE_SYSTEM_PROCESSOR=aarch64

TENSORFLOW_LITE_MAKE_OPTS += _pywrap_tensorflow_interpreter_wrapper

TENSORFLOW_LITE_POST_INSTALL_TARGET_HOOKS = TENSORFLOW_LITE_INSTALL_TFLITE_RUNTIME

define TENSORFLOW_LITE_INSTALL_TFLITE_RUNTIME
# Install all tflite-runtime files manually
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/types/libabsl_bad_optional_access.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/types/libabsl_bad_variant_access.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/base/libabsl_base.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/base/libabsl_log_severity.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/base/libabsl_malloc_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/base/libabsl_raw_logging_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/base/libabsl_spinlock_wait.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/base/libabsl_throw_delegate.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/hash/libabsl_city.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/hash/libabsl_hash.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/hash/libabsl_low_level_hash.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/time/libabsl_civil_time.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/time/libabsl_time.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/time/libabsl_time_zone.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/strings/libabsl_cord_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/strings/libabsl_cord.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/strings/libabsl_cordz_functions.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/strings/libabsl_cordz_handle.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/strings/libabsl_cordz_info.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/strings/libabsl_str_format_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/strings/libabsl_strings_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/strings/libabsl_strings.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/debugging/libabsl_debugging_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/debugging/libabsl_demangle_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/debugging/libabsl_stacktrace.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/debugging/libabsl_symbolize.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/profiling/libabsl_exponential_biased.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags_commandlineflag_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags_commandlineflag.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags_config.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags_marshalling.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags_private_handle_accessor.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags_program_name.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags_reflection.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/flags/libabsl_flags.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/synchronization/libabsl_graphcycles_internal.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/synchronization/libabsl_synchronization.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/container/libabsl_hashtablez_sampler.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/container/libabsl_raw_hash_set.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/numeric/libabsl_int128.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/abseil-cpp-build/absl/status/libabsl_status.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/cpuinfo-build/libcpuinfo.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/farmhash-build/libfarmhash.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/fft2d-build/libfft2d_fftsg2d.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/fft2d-build/libfft2d_fftsg.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_deps/xnnpack-build/libXNNPACK.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/pthreadpool/libpthreadpool.so \
$(TARGET_DIR)/usr/lib/
$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/libtensorflow-lite.so \
$(TARGET_DIR)/usr/lib/

mkdir -p $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime
mkdir -p $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime-2.9.1-py3.10.egg-info

$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/buildroot-build/_pywrap_tensorflow_interpreter_wrapper.so \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime/

$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/python/interpreter.py \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime/

$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/python/metrics/metrics_interface.py \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime/

$(INSTALL) -D -m 755 $(@D)/$(TENSORFLOW_LITE_SUBDIR)/python/metrics/metrics_portable.py \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime/

$(INSTALL) -D -m 755 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/tensorflow-lite/tflite_runtime/__init__.py \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime/

$(INSTALL) -D -m 755 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/tensorflow-lite/tflite_runtime/MANIFEST.in \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime/

$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/tensorflow-lite/tflite_runtime-2.9.1-py3.10.egg-info/dependency_links.txt \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime-2.9.1-py3.10.egg-info/

$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/tensorflow-lite/tflite_runtime-2.9.1-py3.10.egg-info/PKG-INFO \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime-2.9.1-py3.10.egg-info/

$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/tensorflow-lite/tflite_runtime-2.9.1-py3.10.egg-info/requires.txt \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime-2.9.1-py3.10.egg-info/

$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/tensorflow-lite/tflite_runtime-2.9.1-py3.10.egg-info/SOURCES.txt \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime-2.9.1-py3.10.egg-info/

$(INSTALL) -D -m 644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/tensorflow-lite/tflite_runtime-2.9.1-py3.10.egg-info/top_level.txt \
$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/tflite_runtime-2.9.1-py3.10.egg-info/

endef

$(eval $(cmake-package))
