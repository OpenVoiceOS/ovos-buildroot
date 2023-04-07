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
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.search_utils import *


CON_DICT = {"cattalk.com,12345,Cat Talk Convo": ["cat", "talk", "convo"],
            "dogreport.com,54321,Dog Report Convo": ["dog", "report", "convo"]}

DOM_DICT = {"cattalk.com": ["cat", "cats", "cattalk", "cat talk"],
            "dogreport.com": ["dog", "dogs", "dogreport", "dog report"]}

MSG_DICT = {"cattalk.com,12345,0,username,sid,how are you doing": ["how", "are", "you", "doing"],
            "dogreport.com,54321,0,username,sid,I love my dog": ["i", "love", "my", "dog"]}


class SearchUtilTests(unittest.TestCase):
    def test_search_con(self):
        results = search_convo_dict(CON_DICT, "cat")
        self.assertIn("cattalk.com,12345,Cat Talk Convo", results)

        results = search_convo_dict(CON_DICT, "convo")
        self.assertIn("cattalk.com,12345,Cat Talk Convo", results)
        self.assertIn("dogreport.com,54321,Dog Report Convo", results)

    def test_search_dom(self):
        results = search_convo_dict(DOM_DICT, "cat")
        self.assertIn("cattalk.com", results)
        self.assertNotIn("dogreport.com", results)

    def test_search_shout(self):
        results = search_convo_dict(MSG_DICT, "dog")
        self.assertIn("dogreport.com,54321,0,username,sid,I love my dog", results)

    # # TODO: Need to document typo handling/search expected results DM
    # def test_search_typo(self):
    #     results = search_convo_dict(MSG_DICT, "dig", handle_typos=True)
    #     self.assertIn("dogreport.com,54321,0,username,sid,I love my dog", results)
    #
    #     results = search_convo_dict(MSG_DICT, "dig", handle_typos=False)
    #     self.assertNotIn("dogreport.com,54321,0,username,sid,I love my dog", results)


if __name__ == '__main__':
    unittest.main()
