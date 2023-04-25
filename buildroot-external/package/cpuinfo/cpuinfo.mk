################################################################################
#
# cpuinfo
#
################################################################################

CPUINFO_VERSION = eb4a6674bfe9cf91b63b9817412ae5f6862c8432
CPUINFO_SITE = $(call github,pytorch,cpuinfo,$(CPUINFO_VERSION))
CPUINFO_LICENSE = BSD-2-Clause
CPUINFO_LICENSE_FILES = LICENSE
CPUINFO_INSTALL_STAGING = YES
CPUINFO_CONF_OPTS = \
	-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
	-DCPUINFO_LIBRARY_TYPE:STRING=shared \
	-DCPUINFO_BUILD_UNIT_TESTS=OFF \
	-DCPUINFO_BUILD_MOCK_TESTS=OFF \
	-DCPUINFO_BUILD_BENCHMARKS=OFF

$(eval $(cmake-package))
