#!/usr/bin/python3


class Album:
    def __init__(self, ids: int) -> None:
        self.__t_list = []
        self.zip_path = None
        self.image = None
        self.album_quality = None
        self.md5_image = None
        self.ids = ids
        self.nb_tracks = None
        self.album_name = None
        self.upc = None
        self.__set_album_md5()

    @property
    def tracks(self):
        return self.__t_list

    def __set_album_md5(self):
        self.album_md5 = f"album/{self.ids}"
