# -*- coding: utf-8 -*-
# This file is part of convertdate.
# http://github.com/fitnr/convertdate
# Licensed under the MIT license:
# http://opensource.org/licenses/MIT
# Copyright (c) 2016, 2020, 2021, 2022 fitnr <fitnr@fakeisthenewreal>
"""
The Convertdate library contains methods and functions for converting dates between
different calendar systems.

It was originally developed as as `Python Date Util <(http://sourceforge.net/projects/pythondateutil/>`__
by Phil Schwartz. It has been significantly updated and expanded.

Most of the original code is ported from
`Fourmilab's calendar converter <http://www.fourmilab.ch/documents/calendar/>`__,
which was developed by John Walker.

The algorithms are believed to be derived from: Meeus, Jean. `Astronomical Algorithms`,
Richmond: Willmann-Bell, 1991 (ISBN 0-943396-35-2)
"""
from . import armenian
from . import bahai
from . import coptic
from . import daycount
from . import dublin
from . import french_republican
from . import gregorian
from . import hebrew
from . import holidays
from . import indian_civil
from . import iso
from . import islamic
from . import julian
from . import julianday
from . import mayan
from . import persian
from . import positivist
from . import ordinal
from . import utils

__version__ = '2.4.0'

__all__ = [
    'holidays',
    'armenian',
    'bahai',
    'coptic',
    'dublin',
    'daycount',
    'french_republican',
    'gregorian',
    'hebrew',
    'indian_civil',
    'islamic',
    'iso',
    'julian',
    'julianday',
    'mayan',
    'persian',
    'positivist',
    'mayan',
    'ordinal',
    'utils',
]
