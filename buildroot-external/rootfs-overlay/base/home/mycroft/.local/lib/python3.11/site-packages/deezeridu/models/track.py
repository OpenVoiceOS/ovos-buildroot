#!/usr/bin/python3
from tempfile import gettempdir
from os.path import isfile


class Track:
    def __init__(
            self,
            tags: dict,
            song_path: str,
            file_format: str,
            quality: str,
            link: str,
            ids: int
    ) -> None:
        self.tags = tags
        self.__set_tags()
        self.song_name = f"{self.music} - {self.artist}"
        self.song_path = song_path
        self.file_format = file_format
        self.quality = quality
        self.link = link
        self.ids = ids
        self.md5_image = None
        self.success = True
        self.__set_track_md5()

    @property
    def image_path(self):
        path = self.song_path + ".jpg"
        if not isfile(path):
            try:
                with open(path, "wb") as f:
                    f.write(self.tags["image"])
            except:
                pass
        return path

    @property
    def track_info(self):
        return {
            "title": self.tags.get("music") or self.song_name,
            "url": self.link,
            "album": self.tags.get("album"),
            "genre": self.tags.get("genre"),
            "artist": self.tags.get("artist"),
            "duration": self.tags.get("duration", 0)
        }

    def __set_tags(self):
        for tag, value in self.tags.items():
            setattr(
                self, tag, value
            )

    def __set_track_md5(self):
        self.track_md5 = f"track/{self.ids}"

    def set_fallback_ids(self, fallback_ids):
        self.fallback_ids = fallback_ids
        self.fallback_track_md5 = f"track/{self.fallback_ids}"
