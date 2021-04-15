################################################################################
#
# wiringpi2
#
################################################################################

WIRINGPI2_VERSION = f66c883d7c75280971a01619cd503d1809754801
WIRINGPI2_SITE = $(call github,WiringPi,WiringPi,$(WIRINGPI2_VERSION))

WIRINGPI2_LICENSE = LGPL-3.0+
WIRINGPI2_LICENSE_FILES = COPYING.LESSER
WIRINGPI2_INSTALL_STAGING = YES

define WIRINGPI2_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/wiringPi all
	$(TARGET_MAKE_ENV) $(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/devLib all
	$(TARGET_MAKE_ENV) $(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/gpio all
endef

define WIRINGPI2_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/wiringPi install DESTDIR=$(STAGING_DIR) PREFIX=/usr LDCONFIG=true
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/devLib install DESTDIR=$(STAGING_DIR) PREFIX=/usr LDCONFIG=true
endef

define WIRINGPI2_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/wiringPi install DESTDIR=$(TARGET_DIR) PREFIX=/usr LDCONFIG=true
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/devLib install DESTDIR=$(TARGET_DIR) PREFIX=/usr LDCONFIG=true
	$(INSTALL) -D -m 0755 $(@D)/gpio/gpio $(TARGET_DIR)/usr/bin/gpio
	$(INSTALL) -D -m 0755 $(@D)/gpio/pintest $(TARGET_DIR)/usr/bin/pintest
endef

$(eval $(generic-package))
