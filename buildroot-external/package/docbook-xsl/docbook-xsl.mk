################################################################################
#
# docbook-xsl
#
################################################################################

DOCBOOK_XSL_VERSION = 1.79.2
DOCBOOK_XSL_SOURCE = docbook-xsl-nons-$(DOCBOOK_XSL_VERSION).tar.bz2
DOCBOOK_XSL_SITE = https://github.com/docbook/xslt10-stylesheets/releases/download/release/$(DOCBOOK_XSL_VERSION)
DOCBOOK_XSL_INSTALL_STAGING = YES

define DOCBOOK_XSL_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION)
	cp -v -R $(@D)/VERSION $(@D)/assembly $(@D)/common $(@D)/eclipse $(@D)/epub $(@D)/epub3 \
		$(@D)/extensions $(@D)/fo $(@D)/highlighting $(@D)/html $(@D)/htmlhelp $(@D)/images \
		$(@D)/javahelp $(@D)/lib $(@D)/manpages $(@D)/params $(@D)/profiling $(@D)/roundtrip \
		$(@D)/slides $(@D)/template $(@D)/tests $(@D)/tools $(@D)/webhelp $(@D)/website \
		$(@D)/xhtml $(@D)/xhtml-1_1 $(@D)/xhtml5 \
		$(STAGING_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION)

	ln -s $(STAGING_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION)/VERSION \
	$(STAGING_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION)/VERSION.xsl

	ln -s $(STAGING_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION) \
	$(STAGING_DIR)/usr/share/xml/docbook/xsl-stylesheets
endef

define DOCBOOK_XSL_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION)
        cp -v -R $(@D)/VERSION $(@D)/assembly $(@D)/common $(@D)/eclipse $(@D)/epub $(@D)/epub3 \
                $(@D)/extensions $(@D)/fo $(@D)/highlighting $(@D)/html $(@D)/htmlhelp $(@D)/images \
                $(@D)/javahelp $(@D)/lib $(@D)/manpages $(@D)/params $(@D)/profiling $(@D)/roundtrip \
                $(@D)/slides $(@D)/template $(@D)/tests $(@D)/tools $(@D)/webhelp $(@D)/website \
                $(@D)/xhtml $(@D)/xhtml-1_1 $(@D)/xhtml5 \
                $(TARGET_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION)

	ln -s $(TARGET_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION)/VERSION \
        $(TARGET_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION)/VERSION.xsl

	ln -s $(TARGET_DIR)/usr/share/xml/docbook/xsl-stylesheets-nons-$(DOCBOOK_XSL_VERSION) \
        $(TARGET_DIR)/usr/share/xml/docbook/xsl-stylesheets
endef

$(eval $(generic-package))
