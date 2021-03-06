# =============================================================================
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 - 2016 Tobias Röttger <toroettg@gmail.com>
#
# This file is part of SeriesMarker.
#
# SeriesMarker is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# SeriesMarker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SeriesMarker.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================

import unittest

from seriesmarker.test.core import directory_test, window_sort_restore_test, \
    window_state_restore_test


def get_suit():
    core_suits = unittest.TestSuite()

    suites = [
        directory_test.get_suit(),
        window_sort_restore_test.get_suit(),
        window_state_restore_test.get_suit()
    ]

    for suite in suites:
        core_suits.addTests(suite)

    return core_suits


def load_tests(loader, tests, pattern):
    """Enables (graphical) unit testing in PyDev."""
    return get_suit()


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(get_suit())
