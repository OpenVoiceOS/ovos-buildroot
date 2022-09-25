################################################################################
#
# skill-news
#
################################################################################

SKILL_NEWS_VERSION = 263514b74418c76ba87b8aab8bf52380782e9a2a
SKILL_NEWS_SITE = $(call github,OpenVoiceOS,skill-news,$(SKILL_NEWS_VERSION))
SKILL_NEWS_SETUP_TYPE = setuptools
SKILL_NEWS_LICENSE_FILES = LICENSE

$(eval $(python-package))
