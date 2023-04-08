#!/usr/bin/python3

from binascii import (
	a2b_hex as __a2b_hex,
	b2a_hex as __b2a_hex
)
from hashlib import md5 as __md5

from Cryptodome.Cipher.AES import (
	new as __newAES,
	MODE_ECB as __MODE_ECB
)
from Cryptodome.Cipher.Blowfish import (
	new as __newBlowfish,
	MODE_CBC as __MODE_CBC
)

__secret_key = "g4el58wc0zvf9na1"
__secret_key2 = b"jo6aey6haid2Teih"
__idk = __a2b_hex("0001020304050607")


def md5hex(data: str):
    hashed = __md5(
        data.encode()
    ).hexdigest()

    return hashed


def gen_song_hash(md5, quality, ids, media):
    data = b"\xa4".join(
        a.encode()
        for a in [
            md5, quality, ids, media
        ]
    )

    hashed = (
        __md5(data)
            .hexdigest()
            .encode()
    )

    data = b"\xa4".join(
        [hashed, data]
    ) + b"\xa4"

    if len(data) % 16:
        data += b"\x00" * (16 - len(data) % 16)

    c = __newAES(__secret_key2, __MODE_ECB)

    media_url = __b2a_hex(
        c.encrypt(data)
    ).decode()

    return media_url


def __calcbfkey(songid):
    h = md5hex(songid)

    bfkey = "".join(
        chr(
            ord(h[i]) ^ ord(h[i + 16]) ^ ord(__secret_key[i])
        )

        for i in range(16)
    )

    return bfkey


def __blowfishDecrypt(data, key):
    c = __newBlowfish(
        key.encode(), __MODE_CBC, __idk
    )

    return c.decrypt(data)


def decryptfile(content, key, name):
    key = __calcbfkey(key)
    decrypted_audio = open(name, "wb")
    seg = 0

    for data in content:
        if (
                (seg % 3) == 0
        ) and (
                len(data) == 2048
        ):
            data = __blowfishDecrypt(data, key)

        decrypted_audio.write(data)
        seg += 1

    decrypted_audio.close()
