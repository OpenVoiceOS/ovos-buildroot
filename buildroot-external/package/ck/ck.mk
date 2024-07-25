################################################################################
#
# ck
#
################################################################################

CK_VERSION = 0.7.2
CK_SITE = $(call github,concurrencykit,ck,$(CK_VERSION))
CK_LICENSE = Apache-2.0
CK_LICENSE_FILES = LICENSE

CK_INSTALL_STAGING = YES

CK_CONF_OPTS = \
	--platform=$(BR2_ARCH) \
	--prefix="/usr"

CK_LDFLAGS = -Wl,-soname,libck.so.0  -shared -fPIC
CK_CFLAGS = $(TARGET_CFLAGS) -std=gnu99 -fPIC

ifeq ($(BR2_arm)$(BR2_ARM_CPU_ARMV6),yy)
CK_CONF_OPTS += --profile="arm"
CK_CFLAGS +=  -march=armv6k
else ifeq ($(BR2_arm)$(BR2_ARM_CPU_ARMV7A),yy)
CK_CONF_OPTS += --profile="arm"
CK_CFLAGS +=  -march=armv7-a
else ifeq ($(BR2_arm),y)
CK_CONF_OPTS += --profile="arm"
else ifeq ($(BR2_aarch64),y)
CK_CONF_OPTS += --profile="aarch64"
else ifeq ($(BR2_powerpc),y)
CK_CONF_OPTS += --profile="ppc"
else ifeq ($(BR2_powerpc64)$(BR2_powerpc64le),y)
CK_CONF_OPTS += --profile="ppc64"
else ifeq ($(BR2_s390x),y)
CK_CONF_OPTS += --profile="s390x"
else ifeq ($(BR2_x86_64),y)
CK_CONF_OPTS += --profile="x86_64"
CK_LDFLAGS += -m64
else ifeq ($(BR2_i386),y)
CK_CONF_OPTS += --profile="x86"
else ifeq ($(BR2_sparc_v9),y)
CK_CONF_OPTS += --profile="sparcv9"
endif

define CK_CONFIGURE_CMDS
	cd $(@D); \
		$(TARGET_CONFIGURE_OPTS) \
		LD=$(TARGET_CC) \
		CC=$(TARGET_CC) \
		LDFLAGS="$(CK_LDFLAGS)" \
		CFLAGS="$(CK_CFLAGS)" \
		ALL_LIBS="libck.so" \
		INSTALL_LIBS="install-so" \
		PTHREAD_CFLAGS="-pthread" \
		./configure $(CK_CONF_OPTS)
endef

define CK_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)
endef

define CK_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR=$(TARGET_DIR) install
endef

define CK_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR=$(STAGING_DIR) install
endef

$(eval $(generic-package))
