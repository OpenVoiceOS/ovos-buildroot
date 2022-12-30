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

import os
import sys
import random
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.cache_utils import *


class CacheUtilTests(unittest.TestCase):

    def setUp(self) -> None:
        self.lru_cache = LRUCache()

    # def tearDown(self) -> None:
    #     self.lru_cache.clear()

    def test_put(self):
        max_size = self.lru_cache._capacity

        self.lru_cache.put("1", 1)
        self.assertEqual(len(self.lru_cache), 1)

        for i in range(2, max_size+2):
            self.lru_cache.put(str(i), i)
        self.assertEqual(len(self.lru_cache), max_size)
        self.assertNotIn("1", self.lru_cache.cache)

        random_i = random.randint(0, max_size)
        self.lru_cache.put(str(random_i), random_i)
        self.assertEqual(random_i, self.lru_cache.cache.popitem()[1])

    def test_get(self):
        hits = self.lru_cache.hits
        missed = self.lru_cache.missed
        key = random.randint(0, self.lru_cache._capacity - 1)
        invalid_key = "a"

        for i in range(self.lru_cache._capacity):
            self.lru_cache.put(str(i), i)

        for i in range(self.lru_cache._capacity):
            self.assertIsNotNone(self.lru_cache.get(str(i)))

        self.assertIsNotNone(self.lru_cache.get('0'))
        self.assertIsNotNone(self.lru_cache.get(str(self.lru_cache._capacity - 1)))
        self.assertIsNone(self.lru_cache.get(str(self.lru_cache._capacity)))
        result = self.lru_cache.get(str(key))
        self.assertIsNotNone(result)
        self.assertEqual(result, key)

        self.assertEqual(self.lru_cache.hits, hits + 3 + self.lru_cache._capacity)
        self.assertEqual(self.lru_cache.cache.popitem()[1], key)

        self.assertIsNone(self.lru_cache.get(invalid_key))
        self.assertEqual(self.lru_cache.missed, missed + 2)

    def test_clear(self):
        for i in range(self.lru_cache._capacity):
            self.lru_cache.put(str(i), i)

        self.lru_cache.clear()
        self.assertEqual(len(self.lru_cache), 0)

    def test_clear_full(self):
        for i in range(self.lru_cache._capacity):
            self.lru_cache.put(str(i), i)
        self.lru_cache._missed = self.lru_cache._hits = 10
        init_time = self.lru_cache._init_time

        self.lru_cache.clear_full()

        self.assertEqual(len(self.lru_cache), 0)
        self.assertEqual(self.lru_cache.hits, 0)
        self.assertEqual(self.lru_cache.missed, 0)
        self.assertNotEqual(init_time, self.lru_cache._init_time)

    def test_jsonify(self):
        for i in range(self.lru_cache._capacity):
            self.lru_cache.put(str(i), i)

        with self.assertRaises(TypeError):
            json.dumps(self.lru_cache)

        j = self.lru_cache.jsonify()
        self.assertIsInstance(j, str)

    def jsonify_metrics(self):
        j = self.lru_cache.jsonify_metrics()
        self.assertIsInstance(j, str)


if __name__ == '__main__':
    unittest.main()
