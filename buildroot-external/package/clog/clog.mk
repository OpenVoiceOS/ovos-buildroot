################################################################################
#
# clog
#
################################################################################

CLOG_VERSION = 4b5a76c4de21265ddba98fc8f259e136ad11411b
CLOG_SITE = $(call github,pytorch,cpuinfo,$(CLOG_VERSION))
CLOG_SUBDIR = deps/clog
CLOG_LICENSE = BSD-2-Clause
CLOG_LICENSE_FILES = LICENSE

CLOG_SUPPORTS_IN_SOURCE_BUILD = NO
CLOG_CONF_OPTS = -DCLOG_BUILD_TESTS=OFF

CLOG_INSTALL_STAGING = YES
CLOG_INSTALL_TARGET = NO

$(eval $(cmake-package))
