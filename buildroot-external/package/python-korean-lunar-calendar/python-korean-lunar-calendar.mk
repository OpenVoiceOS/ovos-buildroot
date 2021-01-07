################################################################################
#
# python-korean-lunar-calendar
#
################################################################################

PYTHON_KOREAN_LUNAR_CALENDAR_VERSION = 0.2.1
PYTHON_KOREAN_LUNAR_CALENDAR_SOURCE = korean_lunar_calendar-$(PYTHON_KOREAN_LUNAR_CALENDAR_VERSION).tar.gz
PYTHON_KOREAN_LUNAR_CALENDAR_SITE = https://files.pythonhosted.org/packages/fa/c4/2f0f2329098ee24f629c3ad4dcb210fbedb52e51fa6348ebdcbd7af2151b
PYTHON_KOREAN_LUNAR_CALENDAR_SETUP_TYPE = setuptools
PYTHON_KOREAN_LUNAR_CALENDAR_LICENSE = MIT
PYTHON_KOREAN_LUNAR_CALENDAR_LICENSE_FILES = LICENSE

$(eval $(python-package))
