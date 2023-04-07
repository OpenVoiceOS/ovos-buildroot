from bs4 import BeautifulSoup
from py_bandcamp.session import SESSION as requests
from py_bandcamp.utils import extract_ldjson_blob, get_props


class BandcampTrack:
    def __init__(self, data, parse=True):
        self._url = data.get("url")
        self._data = data or {}
        self._page_data = {}
        if parse:
            self.parse_page()
        if not self.url:
            raise ValueError("bandcamp url is not set")

    def parse_page(self):
        self._page_data = self.get_track_data(self.url)
        return self._page_data

    @staticmethod
    def from_url(url):
        return BandcampTrack({"url": url})

    @property
    def url(self):
        return self._url or self.data.get("url")

    @property
    def album(self):
        return self.get_album(self.url)

    @property
    def artist(self):
        return self.get_artist(self.url)

    @property
    def data(self):
        for k, v in self._page_data.items():
            self._data[k] = v
        return self._data

    @property
    def title(self):
        return self.data.get("title") or self.data.get("name") or \
               self.url.split("/")[-1]

    @property
    def image(self):
        return self.data.get("image")

    @property
    def track_num(self):
        return self.data.get("tracknum")

    @property
    def duration(self):
        return self.data.get("duration_secs") or 0

    @property
    def stream(self):
        return self.data.get("file_mp3-128")

    @staticmethod
    def get_album(url):
        data = extract_ldjson_blob(url, clean=True)
        if data.get('inAlbum'):
            return BandcampAlbum({
                "title": data['inAlbum'].get('name'),
                "url": data['inAlbum'].get('id', url).split("#")[0],
                'type': data['inAlbum'].get("type"),
            })

    @staticmethod
    def get_artist(url):
        data = extract_ldjson_blob(url, clean=True)
        d = data.get("byArtist")
        if d:
            return BandcampArtist({
                "title": d.get('name'),
                "url": d.get('id', url).split("#")[0],
                'genre': d.get('genre'),
                "artist_type": d.get('type')
            }, scrap=False)
        return None

    @staticmethod
    def get_track_data(url):
        data = extract_ldjson_blob(url, clean=True)
        kwords = data.get('keywords', "")
        if isinstance(kwords, str):
            kwords = kwords.split(", ")
        track = {
            'dateModified': data.get('dateModified'),
            'datePublished': data.get('datePublished'),
            "url": data.get('id') or url,
            "title": data.get("name"),
            "type": data.get("type"),
            'image': data.get('image'),
            'keywords': kwords
        }
        for k, v in get_props(data).items():
            track[k] = v
        return track

    def __repr__(self):
        return self.__class__.__name__ + ":" + self.title

    def __str__(self):
        return self.url


class BandcampAlbum:
    def __init__(self, data, scrap=True):
        self._url = data.get("url")
        self._data = data or {}
        self._page_data = {}
        if scrap:
            self.scrap()
        if not self.url:
            raise ValueError("bandcamp url is not set")

    def scrap(self):
        self._page_data = self.get_album_data(self.url)
        return self._page_data

    @staticmethod
    def from_url(url):
        return BandcampAlbum({"url": url})

    @property
    def image(self):
        return self.data.get("image")

    @property
    def url(self):
        return self._url or self.data.get("url")

    @property
    def title(self):
        return self.data.get("title") or self.data.get("name") or \
               self.url.split("/")[-1]

    @property
    def releases(self):
        return self.get_releases(self.url)

    @property
    def artist(self):
        return self.get_artist(self.url)

    @property
    def keywords(self):
        return self.data.get("keywords") or []

    @property
    def tracks(self):
        return self.get_tracks(self.url)

    @property
    def featured_track(self):
        if not len(self.tracks):
            return None
        num = self.data.get('featured_track_num', 1) or 1
        return self.tracks[int(num) - 1]

    @property
    def comments(self):
        return self.get_comments(self.url)

    @property
    def data(self):
        for k, v in self._page_data.items():
            self._data[k] = v
        return self._data

    @staticmethod
    def get_releases(url):
        data = extract_ldjson_blob(url, clean=True)
        releases = []
        for d in data.get("albumRelease", []):
            release = {
                "description": d.get("description"),
                'image': d.get('image'),
                "title": d.get('name'),
                "url": d.get('id', url).split("#")[0],
                'format': d.get('musicReleaseFormat'),
            }
            releases.append(release)
        return releases

    @staticmethod
    def get_artist(url):
        data = extract_ldjson_blob(url, clean=True)
        d = data.get("byArtist")
        if d:
            return BandcampArtist({
                "description": d.get("description"),
                'image': d.get('image'),
                "title": d.get('name'),
                "url": d.get('id', url).split("#")[0],
                'genre': d.get('genre'),
                "artist_type": d.get('type')
            }, scrap=False)
        return None

    @staticmethod
    def get_tracks(url):
        data = extract_ldjson_blob(url, clean=True)
        if not data.get("track"):
            return []

        data = data['track']

        tracks = []

        for d in data.get('itemListElement', []):
            d = d['item']
            track = {
                "title": d.get('name'),
                "url": d.get('id') or url,
                'type': d.get('type'),
            }
            for k, v in get_props(d).items():
                track[k] = v
            tracks.append(BandcampTrack(track, parse=False))
        return tracks

    @staticmethod
    def get_comments(url):
        data = extract_ldjson_blob(url, clean=True)
        comments = []
        for d in data.get("comment", []):
            comment = {
                "text": d["text"],
                'image': d["author"].get("image"),
                "author": d["author"]["name"]
            }
            comments.append(comment)
        return comments

    @staticmethod
    def get_album_data(url):
        data = extract_ldjson_blob(url, clean=True)
        props = get_props(data)
        kwords = data.get('keywords', "")
        if isinstance(kwords, str):
            kwords = kwords.split(", ")
        return {
            'dateModified': data.get('dateModified'),
            'datePublished': data.get('datePublished'),
            'description': data.get('description'),
            "url": data.get('id') or url,
            "title": data.get("name"),
            "type": data.get("type"),
            "n_tracks": data.get('numTracks'),
            'image': data.get('image'),
            'featured_track_num': props.get('featured_track_num'),
            'keywords': kwords
        }

    def __repr__(self):
        return self.__class__.__name__ + ":" + self.title

    def __str__(self):
        return self.url


class BandcampLabel:
    def __init__(self, data, scrap=True):
        self._url = data.get("url")
        self._data = data or {}
        self._page_data = {}
        if scrap:
            self.scrap()
        if not self.url:
            raise ValueError("bandcamp url is not set")

    def scrap(self):
        self._page_data = {}  # TODO
        return self._page_data

    @staticmethod
    def from_url(url):
        return BandcampTrack({"url": url})

    @property
    def url(self):
        return self._url or self.data.get("url")

    @property
    def data(self):
        for k, v in self._page_data.items():
            self._data[k] = v
        return self._data

    @property
    def name(self):
        return self.data.get("title") or self.data.get("name") or \
               self.url.split("/")[-1]

    @property
    def location(self):
        return self.data.get("location")

    @property
    def tags(self):
        return self.data.get("tags") or []

    @property
    def image(self):
        return self.data.get("image")

    def __repr__(self):
        return self.__class__.__name__ + ":" + self.name

    def __str__(self):
        return self.url


class BandcampArtist:
    def __init__(self, data, scrap=True):
        self._url = data.get("url")
        self._data = data or {}
        self._page_data = {}
        if scrap:
            self.scrap()

    def scrap(self):
        self._page_data = {}  # TODO
        return self._page_data

    @property
    def featured_album(self):
        return BandcampAlbum.from_url(self.url + "/releases")

    @property
    def featured_track(self):
        if not self.featured_album:
            return None
        return self.featured_album.featured_track

    @staticmethod
    def get_albums(url):
        albums = []
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        for album in soup.find_all("a"):
            album_url = album.find("p", {"class": "title"})
            if album_url:
                title = album_url.text.strip()
                art = album.find("div", {"class": "art"}).find("img")["src"]
                album_url = url + album["href"]
                album = BandcampAlbum({"album_name": title,
                                       "image": art,
                                       "url": album_url})
                albums.append(album)
        return albums

    @property
    def albums(self):
        return self.get_albums(self.url)

    @staticmethod
    def from_url(url):
        return BandcampTrack({"url": url})

    @property
    def url(self):
        return self._url or self.data.get("url")

    @property
    def data(self):
        for k, v in self._page_data.items():
            self._data[k] = v
        return self._data

    @property
    def name(self):
        return self.data.get("title") or self.data.get("name") or \
               self.url.split("/")[-1]

    @property
    def location(self):
        return self.data.get("location")

    @property
    def genre(self):
        return self.data.get("genre")

    @property
    def tags(self):
        return self.data.get("tags") or []

    @property
    def image(self):
        return self.data.get("image")

    def __repr__(self):
        return self.__class__.__name__ + ":" + self.name

    def __str__(self):
        return self.url

    def __eq__(self, other):
        if str(self) == str(other):
            return True
        return False
