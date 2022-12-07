################################################################################
#
# psimd
#
################################################################################

PSIMD_VERSION = 072586a71b55b7f8c584153d223e95687148a900
PSIMD_SITE = $(call github,Maratyszcza,psimd,$(PSIMD_VERSION))
PSIMD_LICENSE = BSD-2-Clause
PSIMD_LICENSE_FILES = LICENSE

PSIMD_SUPPORTS_IN_SOURCE_BUILD = NO

PSIMD_INSTALL_STAGING = YES
PSIMD_INSTALL_TARGET = NO

$(eval $(cmake-package))
