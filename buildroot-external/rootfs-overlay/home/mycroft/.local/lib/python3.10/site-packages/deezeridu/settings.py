#!/usr/bin/python3

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Accept-Language": "en-US;q=0.5,en;q=0.3"
}

method_saves = ["0", "1", "2"]

qualities = {
    "FLAC": {
        "n_quality": "9",
        "f_format": ".flac",
        "s_quality": "FLAC"
    },

    "MP3_320": {
        "n_quality": "3",
        "f_format": ".mp3",
        "s_quality": "320"
    },

    "MP3_128": {
        "n_quality": "1",
        "f_format": ".mp3",
        "s_quality": "128"
    }
}
