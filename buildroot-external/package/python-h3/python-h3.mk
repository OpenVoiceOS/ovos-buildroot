################################################################################
#
# python-h3
#
################################################################################

PYTHON_H3_VERSION = 3.7.6
PYTHON_H3_SOURCE = h3-$(PYTHON_H3_VERSION).tar.gz
PYTHON_H3_SITE = https://files.pythonhosted.org/packages/0e/92/30070479f7c41d66dc5f0ac44298eaedf4a7dad722348dac82d6dcc7ddd8
PYTHON_H3_SETUP_TYPE = setuptools
PYTHON_H3_LICENSE = MIT
PYTHON_H3_LICENSE_FILES = LICENSE
PYTHON_H3_DEPENDENCIES = host-python-scikit-build host-python-wheel host-python-distro
PYTHON_H3_BUILD_OPTS = -DPython3_INCLUDE_DIR:PATH=$(STAGING_DIR)/usr/include/python$(PYTHON3_VERSION_MAJOR) \
			-DPYTHON_INCLUDE_DIR:PATH=$(STAGING_DIR)/usr/include/python$(PYTHON3_VERSION_MAJOR) \
			-DBUILD_SHARED_LIBS=ON
PYTHON_H3_INSTALL_TARGET_OPTS = -DPython3_INCLUDE_DIR:PATH=$(STAGING_DIR)/usr/include/python$(PYTHON3_VERSION_MAJOR) \
                        -DPYTHON_INCLUDE_DIR:PATH=$(STAGING_DIR)/usr/include/python$(PYTHON3_VERSION_MAJOR) \
                        -DBUILD_SHARED_LIBS=ON

$(eval $(python-package))
