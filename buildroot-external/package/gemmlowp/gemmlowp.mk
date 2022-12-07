################################################################################
#
# gemmlowp
#
################################################################################

GEMMLOWP_VERSION = 08e4bb339e34017a0835269d4a37c4ea04d15a69
GEMMLOWP_SITE = $(call github,google,gemmlowp,$(GEMMLOWP_VERSION))
GEMMLOWP_LICENSE = Apache-2.0
GEMMLOWP_LICENSE_FILES = LICENSE
GEMMLOWP_INSTALL_STAGING = YES
GEMMLOWP_INSTALL_TARGET = NO
GEMMLOWP_SUBDIR = contrib

$(eval $(cmake-package))
