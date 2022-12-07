################################################################################
#
# cpuinfo
#
################################################################################

CPUINFO_VERSION = de2fa78ebb431db98489e78603e4f77c1f6c5c57
CPUINFO_SITE = $(call github,pytorch,cpuinfo,$(CPUINFO_VERSION))
CPUINFO_LICENSE = BSD-2-Clause
CPUINFO_LICENSE_FILES = LICENSE
CPUINFO_INSTALL_STAGING = YES
CPUINFO_SUPPORTS_IN_SOURCE_BUILD = NO

CPUINFO_CONF_OPTS = -DCPUINFO_BUILD_UNIT_TESTS=OFF \
		    -DCPUINFO_BUILD_MOCK_TESTS=OFF \
		    -DCPUINFO_BUILD_BENCHMARKS=OFF

$(eval $(cmake-package))
