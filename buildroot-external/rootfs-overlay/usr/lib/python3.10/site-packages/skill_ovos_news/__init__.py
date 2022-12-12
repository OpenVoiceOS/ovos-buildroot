import re
from datetime import timedelta
from os.path import join, dirname

import feedparser
import requests
from mycroft.util.time import now_local
from ovos_plugin_common_play.ocp import MediaType, PlaybackType, \
    MatchConfidence
from ovos_plugin_common_play.ocp.stream_handlers import get_rss_first_stream
from ovos_utils.log import LOG
from ovos_utils.parse import match_one, MatchStrategy
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
from pytz import timezone


# news uri extractors
def tsf():
    """Custom inews fetcher for TSF news."""
    feed = ('https://www.tsf.pt/stream/audio/{year}/{month:02d}/'
            'noticias/{day:02d}/not{hour:02d}.mp3')
    uri = None
    i = 0
    status = 404
    date = now_local(timezone('Portugal'))
    while status != 200 and i < 6:
        uri = feed.format(hour=date.hour, year=date.year,
                          month=date.month, day=date.day)
        status = requests.get(uri).status_code
        date -= timedelta(hours=1)
        i += 1
    if status != 200:
        return None
    return uri


def gpb():
    """Custom news fetcher for GBP news."""
    feed = 'http://feeds.feedburner.com/gpbnews/GeorgiaRSS?format=xml'
    data = feedparser.parse(feed)
    next_link = None
    for entry in data['entries']:
        # Find the first mp3 link with "GPB {time} Headlines" in title
        if 'GPB' in entry['title'] and 'Headlines' in entry['title']:
            next_link = entry['links'][0]['href']
            break
    html = requests.get(next_link)
    # Find the first mp3 link
    # Note that the latest mp3 may not be news,
    # but could be an interview, etc.
    mp3_find = re.search(r'href="(?P<mp3>.+\.mp3)"'.encode(), html.content)
    if mp3_find is None:
        return None
    url = mp3_find.group('mp3').decode('utf-8')
    return url


def npr():
    url = "https://www.npr.org/rss/podcast.php?id=500005"
    feed = get_rss_first_stream(url)
    if feed:
        return feed["uri"].split("?")[0]


# Unified News Skill
class NewsSkill(OVOSCommonPlaybackSkill):
    # default feeds per language (optional)
    langdefaults = {
        "pt-pt": "TSF",
        "es": "RNE",
        "en-gb": "BBC",
        "en-us": "NPR"
    }
    # all news streams
    lang2news = {
        "en-us": {
            "GPB": {
                "aliases": ["Georgia Public Broadcasting", "GPB",
                            "Georgia Public Radio"],
                "uri": gpb,
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "playback": PlaybackType.AUDIO,
                "media_type": MediaType.NEWS,
                "image": join(dirname(__file__), "ui", "images", "gpb.png"),
                "secondary_langs": ["en"]
            },
            "AP": {
                "aliases": ["AP Hourly Radio News", "Associated Press",
                            "Associated Press News",
                            "Associated Press Radio News",
                            "Associated Press Hourly Radio News"],
                "uri": "rss//https://www.spreaker.com/show/1401466/episodes/feed",
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "image": join(dirname(__file__), "ui", "images", "AP.png"),
                "playback": PlaybackType.AUDIO,
                "media_type": MediaType.NEWS,
                "secondary_langs": ["en"]
            },
            "FOX": {
                "aliases": ["FOX News", "FOX", "Fox News Channel"],
                "uri": "rss//http://feeds.foxnewsradio.com/FoxNewsRadio",
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "playback": PlaybackType.AUDIO,
                "media_type": MediaType.NEWS,
                "image": join(dirname(__file__), "ui", "images", "FOX.png"),
                "secondary_langs": ["en"]
            },
            "NPR": {
                "aliases": ["NPR News", "NPR", "National Public Radio",
                            "National Public Radio News", "NPR News Now"],
                "uri": npr,
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "image": join(dirname(__file__), "ui", "images", "NPR.png"),
                "playback": PlaybackType.AUDIO,
                "media_type": MediaType.NEWS,
                "secondary_langs": ["en"]
            },
            "PBS": {
                "aliases": ["PBS News", "PBS", "PBS NewsHour", "PBS News Hour",
                            "National Public Broadcasting Service",
                            "Public Broadcasting Service News"],
                "uri": "rss//https://www.pbs.org/newshour/feeds/rss/podcasts/show",
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "playback": PlaybackType.AUDIO,
                "media_type": MediaType.NEWS,
                "image": join(dirname(__file__), "ui", "images", "PBS.png"),
                "secondary_langs": ["en"]
            }
        },
        "en-gb": {
            "BBC": {
                "aliases": ["British Broadcasting Corporation", "BBC",
                            "BBC News"],
                "uri": "rss//https://podcasts.files.bbci.co.uk/p02nq0gn.rss",
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "playback": PlaybackType.AUDIO,
                "media_type": MediaType.NEWS,
                "image": join(dirname(__file__), "ui", "images", "BBC.png"),
                "secondary_langs": ["en"]
            }
        },
        "en-ca": {
            "CBC": {
                "aliases": ["Canadian Broadcasting Corporation", "CBC",
                            "CBC News"],
                "uri": "rss//https://www.cbc.ca/podcasting/includes/hourlynews.xml",
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "playback": PlaybackType.AUDIO,
                "media_type": MediaType.NEWS,
                "image": join(dirname(__file__), "ui", "images", "CBC.png"),
                "secondary_langs": ["en"]
            }
        },
        "pt-pt": {
            "TSF": {
                "aliases": ["TSF", "TSF Rádio Notícias", "TSF Notícias"],
                "uri": tsf,
                "media_type": MediaType.NEWS,
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "playback": PlaybackType.AUDIO,
                "image": join(dirname(__file__), "ui", "images", "tsf.png"),
                "secondary_langs": ["pt"]
            }
        },
        "de": {
            "OE3": {
                "aliases": ["OE3", "Ö3 Nachrichten"],
                "uri": "https://oe3meta.orf.at/oe3mdata/StaticAudio/Nachrichten.mp3",
                "media_type": MediaType.NEWS,
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "image": join(dirname(__file__), "ui", "images", "oe3.jpeg"),
                "playback": PlaybackType.AUDIO
            },
            "DLF": {
                "aliases": ["DLF", "deutschlandfunk"],
                "uri": "rss//https://www.deutschlandfunk.de/podcast-nachrichten.1257.de.podcast.xml",
                "media_type": MediaType.NEWS,
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "image": join(dirname(__file__), "ui", "images", "DLF.png"),
                "playback": PlaybackType.AUDIO
            }
        },
        "nl": {
            "VRT": {
                "aliases": ["VRT Nieuws", "VRT"],
                "uri": "https://progressive-audio.lwc.vrtcdn.be/content/fixed/11_11niws-snip_hi.mp3",
                "media_type": MediaType.NEWS,
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "image": join(dirname(__file__), "ui", "images", "vrt.png"),
                "playback": PlaybackType.AUDIO
            }
        },
        "sv": {
            "Ekot": {
                "aliases": ["Ekot"],
                "uri": "rss//https://api.sr.se/api/rss/pod/3795",
                "media_type": MediaType.NEWS,
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "image": join(dirname(__file__), "ui", "images", "Ekot.png"),
                "playback": PlaybackType.AUDIO
            }
        },
        "es": {
            "RNE": {
                "aliases": ["RNE", "National Spanish Radio",
                            "Radio Nacional de España"],
                "media_type": MediaType.NEWS,
                "uri": "rss//http://api.rtve.es/api/programas/36019/audios.rs",
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "image": join(dirname(__file__), "ui", "images", "rne.png"),
                "playback": PlaybackType.AUDIO
            }
        },
        "fi": {
            "YLE": {
                "aliases": ["YLE", "YLE News Radio"],
                "uri": "rss//https://feeds.yle.fi/areena/v1/series/1-1440981.rss",
                "media_type": MediaType.NEWS,
                "match_types": [MediaType.NEWS,
                                MediaType.RADIO],
                "image": join(dirname(__file__), "ui", "images", "Yle.png"),
                "playback": PlaybackType.AUDIO
            }
        }
    }

    def __init__(self):
        super().__init__("News")
        self.supported_media = [MediaType.GENERIC,
                                MediaType.NEWS]
        self.skill_icon = join(dirname(__file__), "ui", "news.png")
        self.default_bg = join(dirname(__file__), "ui", "bg.jpg")

    def clean_phrase(self, phrase):
        phrase = self.remove_voc(phrase, "news")

        phrase = self.remove_voc(phrase, "pt-pt")
        phrase = self.remove_voc(phrase, "en-us")
        phrase = self.remove_voc(phrase, "en-ca")
        phrase = self.remove_voc(phrase, "en-gb")
        phrase = self.remove_voc(phrase, "es")
        phrase = self.remove_voc(phrase, "fi")
        phrase = self.remove_voc(phrase, "de")
        phrase = self.remove_voc(phrase, "sv")
        phrase = self.remove_voc(phrase, "nl")
        phrase = self.remove_voc(phrase, "en")

        return phrase.strip()

    def match_lang(self, phrase):
        langs = []
        if self.voc_match(phrase, "pt-pt"):
            langs.append("pt-pt")
        if self.voc_match(phrase, "en-us"):
            langs.append("en-us")
        if self.voc_match(phrase, "en-gb"):
            langs.append("en-gb")
        if self.voc_match(phrase, "en-ca"):
            langs.append("en-ca")
        if self.voc_match(phrase, "en"):
            langs.append("en")
        if self.voc_match(phrase, "es"):
            langs.append("es")
        if self.voc_match(phrase, "de"):
            langs.append("de")
        if self.voc_match(phrase, "nl"):
            langs.append("nl")
        if self.voc_match(phrase, "fi"):
            langs.append("fi")
        if self.voc_match(phrase, "sv"):
            langs.append("sv")

        langs += [l.split("-")[0] for l in langs]
        return langs

    def _score(self, phrase, entry, langs=None, base_score=0):
        score = base_score
        langs = langs or [self.lang]

        # match name
        _, alias_score = match_one(phrase, entry["aliases"],
                                   strategy=MatchStrategy.TOKEN_SORT_RATIO)
        entry["match_confidence"] = score + alias_score * 60

        # match languages
        if entry["lang"] in langs:
            entry["match_confidence"] += 20  # lang bonus
        elif any([lang in entry.get("secondary_langs", [])
                  for lang in langs]):
            entry["match_confidence"] += 10  # smaller lang bonus
        else:
            entry["match_confidence"] -= 20  # wrong language penalty

        # default news feed gets a nice bonus
        if entry.get("is_default"):
            entry["match_confidence"] += 30

        return min([entry["match_confidence"], 100])

    @ocp_featured_media()
    def news_playlist(self):
        entries = []
        default_feeds = []

        # play user preference if set in skill settings
        feed = self.settings.get("default_feed")
        if not feed and self.lang in self.langdefaults:
            feed = self.langdefaults.get(self.lang)

        for l in self.lang2news:
            for k, v in self.lang2news[l].items():
                if k == feed:
                    v["is_default"] = True
                v["lang"] = l
                v["title"] = v.get("title") or k
                v["bg_image"] = v.get("bg_image") or self.default_bg
                v["skill_logo"] = self.skill_icon
                if callable(v["uri"]):
                    try:
                        v["uri"] = v["uri"]()
                    except:
                        LOG.error(f"stream extraction failed for {k}")
                        continue
                if v["uri"]:
                    entries.append(v)
        return entries

    @ocp_search()
    def search_news(self, phrase, media_type):
        """Analyze phrase to see if it is a play-able phrase with this skill.

        Arguments:
            phrase (str): User phrase uttered after "Play", e.g. "some music"
            media_type (MediaType): requested CPSMatchType to media for

        Returns:
            search_results (list): list of dictionaries with result entries
            {
                "match_confidence": MatchConfidence.HIGH,
                "media_type":  CPSMatchType.MUSIC,
                "uri": "https://audioservice.or.gui.will.play.this",
                "playback": PlaybackType.VIDEO,
                "image": "http://optional.audioservice.jpg",
                "bg_image": "http://optional.audioservice.background.jpg"
            }
        """
        base_score = 0
        if media_type == MediaType.NEWS or self.voc_match(phrase, "news"):
            base_score = 50
            if not phrase.strip():
                base_score += 20  # "play the news", no query

        pl = self.news_playlist()
        # playlist result
        yield {
            "match_confidence": base_score,
            "media_type": MediaType.NEWS,
            "playlist": pl,
            "playback": PlaybackType.AUDIO,
            "image": self.skill_icon,
            "bg_image": self.skill_icon,
            "skill_icon": self.skill_icon,
            "title": "Latest News (Station Playlist)",
            "skill_id": self.skill_id
        }

        # score individual results
        langs = self.match_lang(phrase) or [self.lang, self.lang.split("-")[0]]
        phrase = self.clean_phrase(phrase)
        if media_type == MediaType.NEWS or (phrase and base_score > MatchConfidence.AVERAGE_LOW):
            for v in pl:
                v["match_confidence"] = self._score(phrase, v, langs=langs, base_score=base_score)
                yield v


def create_skill():
    return NewsSkill()
