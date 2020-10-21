################################################################################
#
# docbook-xml
#
################################################################################

DOCBOOK_XML_VERSION = 4.5
DOCBOOK_XML_SOURCE = docbook-xml_$(DOCBOOK_XML_VERSION).orig.tar.gz
DOCBOOK_XML_SITE = http://snapshot.debian.org/archive/debian/20160728T043443Z/pool/main/d/docbook-xml
DOCBOOK_XML_INSTALL_STAGING = YES

define DOCBOOK_XML_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/etc/xml
	mkdir -p $(STAGING_DIR)/usr/share/xml/docbook/schema/dtd/$(DOCBOOK_XML_VERSION)
	cp -v -R $(@D)/docbook-$(DOCBOOK_XML_VERSION)/* \
		$(STAGING_DIR)/usr/share/xml/docbook/schema/dtd/$(DOCBOOK_XML_VERSION)
	xmlcatalog --create --noout $(STAGING_DIR)/etc/xml/docbook-xml.xml

	xmlcatalog --verbose --noout --add nextCatalog unused \
		file://$(STAGING_DIR)/usr/share/xml/docbook/schema/dtd/$(DOCBOOK_XML_VERSION)/catalog.xml \
		$(STAGING_DIR)/etc/xml/docbook-xml.xml
endef

define DOCBOOK_XML_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/etc/xml
        mkdir -p $(TARGET_DIR)/usr/share/xml/docbook/schema/dtd/$(DOCBOOK_XML_VERSION)
        cp -v -R $(@D)/docbook-$(DOCBOOK_XML_VERSION)/* \
                $(TARGET_DIR)/usr/share/xml/docbook/schema/dtd/$(DOCBOOK_XML_VERSION)
        xmlcatalog --create --noout $(TARGET_DIR)/etc/xml/docbook-xml.xml

        xmlcatalog --verbose --noout --add nextCatalog unused \
                file://$(TARGET_DIR)/usr/share/xml/docbook/schema/dtd/$(DOCBOOK_XML_VERSION)/catalog.xml \
                $(TARGET_DIR)/etc/xml/docbook-xml.xml
endef

$(eval $(generic-package))
