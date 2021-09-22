################################################################################
#
# python-pycpuinfo
#
################################################################################

PYTHON_PYCPUINFO_VERSION = 8.0.0
PYTHON_PYCPUINFO_SOURCE = py-cpuinfo-$(PYTHON_PYCPUINFO_VERSION).tar.gz
PYTHON_PYCPUINFO_SITE = https://files.pythonhosted.org/packages/e6/ba/77120e44cbe9719152415b97d5bfb29f4053ee987d6cb63f55ce7d50fadc
PYTHON_PYCPUINFO_SETUP_TYPE = setuptools
PYTHON_PYCPUINFO_LICENSE = MIT
PYTHON_PYCPUINFO_LICENSE_FILES = LICENSE

$(eval $(python-package))
