################################################################################
#
# skill-ovos-news
#
################################################################################

SKILL_OVOS_NEWS_VERSION = 392d32ebea4cc9cc3ba3371c1fe63c72426d0070
SKILL_OVOS_NEWS_SITE = $(call github,OpenVoiceOS,skill-ovos-news,$(SKILL_OVOS_NEWS_VERSION))
SKILL_OVOS_NEWS_SETUP_TYPE = setuptools
SKILL_OVOS_NEWS_LICENSE_FILES = LICENSE

$(eval $(python-package))
