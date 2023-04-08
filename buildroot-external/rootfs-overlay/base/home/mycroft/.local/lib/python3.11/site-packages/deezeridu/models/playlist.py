#!/usr/bin/python3


class Playlist:
    def __init__(self, tracklist=None) -> None:
        self.__t_list = tracklist or []
        self.zip_path = None

    @property
    def tracks(self):
        return self.__t_list
