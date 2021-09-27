################################################################################
#
# python-scipy
#
################################################################################

PYTHON_SCIPY_VERSION = 1.7.1
PYTHON_SCIPY_SOURCE = scipy-$(PYTHON_SCIPY_VERSION).tar.gz
PYTHON_SCIPY_SITE = https://files.pythonhosted.org/packages/47/33/a24aec22b7be7fdb10ec117a95e1e4099890d8bbc6646902f443fc7719d1
PYTHON_SCIPY_LICENSE = BSD-3-Clause
PYTHON_SCIPY_LICENSE_FILES = LICENSE.txt doc/sphinxext/LICENSE.txt \
			doc/scipy-sphinx-theme/LICENSE.txt
PYTHON_SCIPY_SETUP_TYPE = setuptools
PYTHON_SCIPY_DEPENDENCIES = clapack openblas host-python-numpy \
			host-python-pip host-python-pybind \
			host-python-pythran host-python-gast \
			host-python-beniget host-python-ply

PYTHON_SCIPY_ENV += LDFLAGS="$(TARGET_LDFLAGS) -shared \
			-L$(PYTHON3_PATH)/site-packages/numpy/core/lib"

# must be used to locate 'gfortran'
PYTHON_SCIPY_ENV += F90="$(TARGET_FC)"

# trick to locate 'lapack' and 'blas'
define PYTHON_SCIPY_CONFIGURE_CMDS
	rm -f $(@D)/site.cfg
	echo "[DEFAULT]" >> $(@D)/site.cfg
	echo "library_dirs = $(STAGING_DIR)/usr/lib" >> $(@D)/site.cfg
	echo "include_dirs = $(STAGING_DIR)/usr/include" >> $(@D)/site.cfg
endef

$(eval $(python-package))
