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

from datetime import datetime

import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.location_utils import *


class LocationUtilTests(unittest.TestCase):
    def test_get_coordinates_complete(self):
        coords = get_coordinates({"city": "Kirkland", "state": "Washington", "country": "United States"})
        self.assertIsInstance(coords[0], float)
        self.assertIsInstance(coords[1], float)

    def test_get_coordinates_no_city(self):
        coords = get_coordinates({"state": "Washington", "country": "United States"})
        self.assertIsInstance(coords[0], float)
        self.assertIsInstance(coords[1], float)

    def test_get_coordinates_no_state(self):
        coords = get_coordinates({"city": "Seattle", "country": "United States"})
        self.assertIsInstance(coords[0], float)
        self.assertIsInstance(coords[1], float)

    def test_get_coordinates_no_ccountry(self):
        coords = get_coordinates({"state": "Washington", "city": "Renton"})
        self.assertIsInstance(coords[0], float)
        self.assertIsInstance(coords[1], float)

    def test_get_location_from_coords(self):
        lat = 47.6038321
        lng = -122.3300624
        location = get_location(lat, lng)
        self.assertEqual(len(location), 4)
        self.assertEqual(location, ("Seattle", "King County", "Washington", "United States"))

    def test_get_timezone_from_coords(self):
        lat = 47.6038321
        lng = -122.3300624
        timezone, offset = get_timezone(lat, lng)
        self.assertIsInstance(timezone, str)
        self.assertEqual(timezone, "America/Los_Angeles")
        self.assertIsInstance(offset, float)
        self.assertIn(offset, (-7.0, -8.0))

    def test_to_system_time(self):
        tz_aware_dt = datetime.now(gettz("America/NewYork"))
        system_dt = to_system_time(tz_aware_dt)
        self.assertEqual(system_dt.tzinfo, tzlocal())
        self.assertEqual(tz_aware_dt.timestamp(), system_dt.timestamp())

        tz_aware_dt = datetime.now(gettz("America/Los_Angeles"))
        system_dt = to_system_time(tz_aware_dt)
        self.assertEqual(system_dt.tzinfo, tzlocal())
        self.assertEqual(tz_aware_dt.timestamp(), system_dt.timestamp())

        tz_naiive_dt = datetime.now()
        system_dt = to_system_time(tz_naiive_dt)
        self.assertEqual(system_dt.tzinfo, tzlocal())
        self.assertEqual(tz_naiive_dt.timestamp(), system_dt.timestamp())

    def test_get_full_location(self):
        location_en = get_full_location("Seattle, Washington")
        self.assertIsInstance(location_en, dict)
        self.assertIsInstance(location_en['lat'], str)
        self.assertIsInstance(location_en['lon'], str)
        self.assertIsInstance(location_en['address'], dict)
        self.assertEqual(location_en['address']['city'], "Seattle")
        self.assertEqual(location_en['address']['state'], "Washington")
        self.assertEqual(location_en['address']['country'], "United States")
        self.assertEqual(location_en['address']['country_code'], "us")

        location_es = get_full_location("Seattle, Washington", "es")
        self.assertEqual(location_es['lat'], location_en['lat'])
        self.assertEqual(location_es['lon'], location_en['lon'])
        self.assertEqual(location_es['address']['country'],
                         "Estados Unidos de América")
        self.assertEqual(location_en['address']['country_code'], "us")

        location_from_coords = get_full_location((location_en['lat'],
                                                  location_en['lon']))
        self.assertAlmostEqual(float(location_from_coords['lat']),
                               float(location_en['lat']), 3)
        self.assertAlmostEqual(float(location_from_coords['lon']),
                               float(location_en['lon']), 3)
        self.assertEqual(location_from_coords['address']['city'], "Seattle")
        self.assertEqual(location_from_coords['address']['state'],
                         "Washington")
        self.assertEqual(location_from_coords['address']['country'],
                         "United States")
        self.assertEqual(location_from_coords['address']['country_code'], "us")


if __name__ == '__main__':
    unittest.main()
