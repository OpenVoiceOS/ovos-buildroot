################################################################################
#
# skill-ovos-news
#
################################################################################

SKILL_OVOS_NEWS_VERSION = ff730b234edb5bc4e6b7cc0fb17e0a55f60cf474
SKILL_OVOS_NEWS_SITE = $(call github,OpenVoiceOS,skill-ovos-news,$(SKILL_OVOS_NEWS_VERSION))
SKILL_OVOS_NEWS_SETUP_TYPE = setuptools
SKILL_OVOS_NEWS_LICENSE_FILES = LICENSE

$(eval $(python-package))
