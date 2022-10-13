################################################################################
#
# skill-ovos-news
#
################################################################################

SKILL_OVOS_NEWS_VERSION = 1d53a150b6158bbffd1600626f748b1ecf884ae0
SKILL_OVOS_NEWS_SITE = $(call github,OpenVoiceOS,skill-ovos-news,$(SKILL_OVOS_NEWS_VERSION))
SKILL_OVOS_NEWS_SETUP_TYPE = setuptools
SKILL_OVOS_NEWS_LICENSE_FILES = LICENSE

$(eval $(python-package))
