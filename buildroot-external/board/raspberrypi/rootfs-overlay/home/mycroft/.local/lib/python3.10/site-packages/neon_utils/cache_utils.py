# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import time
from collections import OrderedDict


class LRUCache:
    # TODO user specific cache with a compound key
    def __init__(self, capacity: int = 128):
        self.cache = OrderedDict()
        self._capacity = capacity
        self._hits = 0
        self._missed = 0
        self._init_time = time.time()

    def __len__(self):
        return len(self.cache)

    @property
    def hits(self):
        return self._hits

    @property
    def missed(self):
        return self._missed

    def get(self, key):
        """
        Return the value of the key from cache.
        Increment self._missed in key not in cache, increment self._hits in key in cache
        Args:
            key: a key to look up in cache
        Returns: value associated with the key or None

        """
        if key not in self.cache:
            self._missed += 1
            return None
        else:
            self._hits += 1
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key, value) -> None:
        """
        Put a key-value pair into cache
        Args:
            key: a key to put into cache
            value: a value to put into cache
        Returns:
        """
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self._capacity:
            self.cache.popitem(last=False)

    def clear(self):
        """
        Clear the cache dict
        """
        self.cache = OrderedDict()

    def clear_full(self):
        """
        Clear the cache dict, reset hits, missed and initialization time
        Returns:

        """
        self.clear()
        self._hits = self._missed = 0
        self._init_time = time.time()

    def jsonify(self):
        """
        Dump cache dict into json
        Returns: json-string
        """
        return json.dumps(self.cache)

    def jsonify_metrics(self):
        """
        Dump cache metrics into json
        Returns:

        """
        data = dict()
        data["cache"] = self.cache
        data["hits"] = self.hits
        data["missed"] = self.missed
        data["size"] = self._capacity
        return json.dumps(data)
