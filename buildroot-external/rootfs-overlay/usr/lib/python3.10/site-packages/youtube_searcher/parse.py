import bs4
import re
import json
from youtube_searcher.session import session


def _extract_json_blob(soup):
    # Make sure we always get the correct blob and santize it
    blob = soup.find('script', text=re.compile("ytInitialData"))
    json_data = str(blob)[
                str(blob).find('{\"responseContext\"'):str(blob).find(
                    'module={}')]
    json_data = re.split(r"\};", json_data)[0]
    results = json.loads(json_data + "}")
    return results


def _parse_soup(soup):
    results = _extract_json_blob(soup)

    def parse_channel(data):
        channel_data = {}
        if "channelThumbnailSupportedRenderers" in data:
            channel_data = data["channelThumbnailSupportedRenderers"][
                'channelThumbnailWithLinkRenderer']
            brws = channel_data['navigationEndpoint']['browseEndpoint']
            url = "https://www.youtube.com" + brws.get('canonicalBaseUrl',
                                                       brws['browseId'])
            channel_data = {
                "thumbnail": channel_data['thumbnail']['thumbnails'][-1][
                    "url"],
                "url": url,
                "userId": brws['browseId']
            }
        elif 'ownerText' in data:
            channel_data = data['ownerText']["runs"][0]
            brws = channel_data['navigationEndpoint']['browseEndpoint']
            url = "https://www.youtube.com" + brws.get('canonicalBaseUrl',
                                                       brws['browseId'])
            channel_data = {
                "name": channel_data["text"],
                "userId": brws['browseId'],
                "url": url
            }
        elif 'longBylineText' in data:
            channel_data = data['longBylineText']["runs"][0]
            brws = channel_data['navigationEndpoint']['browseEndpoint']
            url = "https://www.youtube.com" + brws.get('canonicalBaseUrl',
                                                       brws['browseId'])
            channel_data = {
                "name": channel_data["text"],
                "userId": brws['browseId'],
                "url": url
            }
        elif 'shortBylineText' in data:
            channel_data = data['shortBylineText']["runs"][0]
            brws = channel_data['navigationEndpoint']['browseEndpoint']
            url = "https://www.youtube.com" + brws.get('canonicalBaseUrl',
                                                       brws['browseId'])
            channel_data = {
                "name": channel_data["text"],
                "userId": brws['browseId'],
                "url": url
            }
        return channel_data

    def parse_title(data):
        if "title" in data:
            data = data['title']
            if 'simpleText' in data:
                return data['simpleText']
            if "runs" in data:
                return " ".join([r["text"] for r in data["runs"]])
            if 'accessibility' in data:
                return data['accessibility']['accessibilityData']['label']
        return ""

    def parse_description(data):
        if 'descriptionSnippet' in data:
            data = data['descriptionSnippet']
            if 'simpleText' in data:
                return data['simpleText']
            if "runs" in data:
                return " ".join([r["text"] for r in data["runs"]])
            if 'accessibility' in data:
                return data['accessibility']['accessibilityData']['label']
        return parse_title(data)

    def parse_thumbnail(data):
        if "thumbnail" in data:
            return data['thumbnail']['thumbnails'][-1]["url"]
        return ""

    def parse_live(data):
        if 'thumbnailOverlays' in data:
            for overlay in data['thumbnailOverlays']:
                if 'thumbnailOverlayTimeStatusRenderer' not in overlay:
                    continue
                if overlay['thumbnailOverlayTimeStatusRenderer'].get(
                        "style", "") == "LIVE":
                    return True
        return False

    def parse_views(data):
        if 'shortViewCountText' in data:
            data = data['shortViewCountText']
            if "runs" in data:
                return " ".join([r["text"] for r in data["runs"]])
            elif 'simpleText' in data:
                return data['simpleText']
        return ""

    def parse_video(data):
        title = parse_title(data)
        if not title:
            # NOTE: non recorded past live streams/private videos usually have
            # only videoId and sometimes playlistId
            return
        video_data = {
            "videoId": data["videoId"],
            # last one is the larger size
            "thumbnail": parse_thumbnail(data),
            'title': title,
            "description": parse_description(data),
            "url": "https://www.youtube.com/watch?v=" + data["videoId"],
            "channel": parse_channel(data),
            "is_live": parse_live(data),
            "views": parse_views(data),
        }
        if "playlistId" in video_data:
            video_data["playlist"] = parse_playlist(data)
        return video_data

    def parse_playlist(data):
        title = parse_title(data)
        if not title or "playlistId" not in data:
            return {}
        url = f'https://www.youtube.com/playlist?list={data["playlistId"]}'
        return {
            "playlistId": data["playlistId"],
            # last one is the larger size
            "thumbnail": parse_thumbnail(data),
            'title': parse_title(data),
            "description": parse_description(data),
            "url": url,
            "channel": parse_channel(data)
        }

    def parse_dict(data):
        for k, v in data.items():
            if isinstance(v, dict):
                if "playlistId" in v:
                    yield parse_playlist(v)
                if "videoId" in v:
                    yield parse_video(v)
                else:
                    for _ in parse_dict(v):
                        yield _
            elif isinstance(v, list):
                for _ in parse_list(v):
                    yield _

    def parse_list(data):
        for v in data:
            if isinstance(v, dict):
                for _ in parse_dict(v):
                    yield _
            elif isinstance(v, list):
                for _ in parse_list(v):
                    yield _

    return [_ for _ in parse_dict(results) if _]


def extract_videos(url, user_agent='Mozilla/5.0 (X11; Linux x86_64) '
                                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                                   'Chrome/57.0.2987.110 '
                                   'Safari/537.36'):
    headers = {
        'User-Agent': user_agent
    }
    html = session.get(url, headers=headers).text

    soup = bs4.BeautifulSoup(html, 'html.parser')

    for vid in _parse_soup(soup):
        if vid.get("videoId"):
            yield vid


def extract_playlists(url, user_agent='Mozilla/5.0 (X11; Linux x86_64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/57.0.2987.110 '
                                      'Safari/537.36'):
    headers = {
        'User-Agent': user_agent
    }
    html = session.get(url, headers=headers).text

    soup = bs4.BeautifulSoup(html, 'html.parser')
    for plist in _parse_soup(soup):
        if plist.get("playlistId"):
            yield plist


def extract_videos_from_playlists(url, user_agent='Mozilla/5.0 (X11; Linux '
                                                  'x86_64) '
                                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                  'Chrome/57.0.2987.110 '
                                                  'Safari/537.36'):
    for playlist in extract_playlists(url, user_agent):
        for vid in extract_videos(playlist["url"], user_agent):
            yield vid

