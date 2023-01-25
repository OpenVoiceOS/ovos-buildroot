################################################################################
#
# compute-library
#
################################################################################

COMPUTE_LIBRARY_VERSION = v22.11
COMPUTE_LIBRARY_SITE = $(call github,ARM-software,ComputeLibrary,$(COMPUTE_LIBRARY_VERSION))
COMPUTE_LIBRARY_LICENSE = MIT
COMPUTE_LIBRARY_LICENSE_FILES = LICENSE
COMPUTE_LIBRARY_INSTALL_STAGING = YES

COMPUTE_LIBRARY_DEPENDENCIES = \
	host-scons \
	host-pkgconf

COMPUTE_LIBRARY_LDFLAGS = "$(TARGET_LDFLAGS)"
COMPUTE_LIBRARY_CFLAGS = " $(TARGET_CFLAGS)"
COMPUTE_LIBRARY_CXXFLAGS = "$(TARGET_CXXFLAGS)"

COMPUTE_LIBRARY_SCONS_ENV = $(TARGET_CONFIGURE_OPTS)

COMPUTE_LIBRARY_SCONS_OPTS = \
	arch=arm64-v8a \
	Werror=0 \
	debug=0 \
	asserts=0 \
	neon=1 \
        os=linux \
	examples=0 \
	build=cross_compile \
	toolchain_prefix="" \
	embed_kernels=1 \
	extra_cxx_flags="-fPIC"

COMPUTE_LIBRARY_SCONS_ENV += \
	LDFLAGS=$(COMPUTE_LIBRARY_LDFLAGS) \
	CFLAGS=$(COMPUTE_LIBRARY_CFLAGS) \
	CCFLAGS=$(COMPUTE_LIBRARY_CFLAGS) \
	CXXFLAGS=$(COMPUTE_LIBRARY_CXXFLAGS)

define COMPUTE_LIBRARY_BUILD_CMDS
	(cd $(@D); \
	$(COMPUTE_LIBRARY_SCONS_ENV) \
	$(SCONS) \
	$(COMPUTE_LIBRARY_SCONS_OPTS))
endef

define COMPUTE_LIBRARY_INSTALL_STAGING_CMDS
	(cd $(@D); \
	$(COMPUTE_LIBRARY_SCONS_ENV) \
	$(SCONS) \
	$(COMPUTE_LIBRARY_SCONS_OPTS) \
	install_dir="$(STAGING_DIR)/usr")
endef

define COMPUTE_LIBRARY_INSTALL_TARGET_CMDS
	(cd $(@D); \
	$(COMPUTE_LIBRARY_SCONS_ENV) \
	$(SCONS) \
	$(COMPUTE_LIBRARY_SCONS_OPTS) \
	install_dir="$(TARGET_DIR)/usr")
endef

$(eval $(generic-package))
