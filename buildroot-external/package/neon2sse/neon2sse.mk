################################################################################
#
# neon2see
#
################################################################################

NEON2SSE_VERSION = a15b489e1222b2087007546b4912e21293ea86ff
NEON2SSE_SITE = $(call github,intel,arm_neon_2_x86_sse,$(NEON2SSE_VERSION))

NEON2SSE_LICENSE = BSD-2-Clause
NEON2SSE_LICENSE_FILES = LICENSE

NEON2SSE_INSTALL_STAGING = YES
NEON2SSE_INSTALL_TARGET = NO

$(eval $(cmake-package))
