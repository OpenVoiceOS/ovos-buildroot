################################################################################
#
# MycroftOS
#
################################################################################

MYCROFTOS_VERSION = 1.0.0
MYCROFTOS_LICENSE = Apache License 2.0
MYCROFTOS_LICENSE_FILES = $(BR2_EXTERNAL_MYCROFTOS_PATH)/../LICENSE
MYCROFTOS_SITE = $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroftos
MYCROFTOS_SITE_METHOD = local

$(eval $(generic-package))
