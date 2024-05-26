#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

# Copyright © 2023 Pradyumna Paranjape

# This file is part of pywaymon.

# pywaymon is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pywaymon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pywaymon.  If not, see <https://www.gnu.org/licenses/>.
"""Test network data monitor module"""

import unittest

from pywaymon.netio import NetIOStats


class TestNetIO(unittest.TestCase):

    def setUp(self):
        self.seg = NetIOStats()

    def test_frac(self):
        self.seg.get_values()
        self.assertIsNotNone(self.seg._last_check)
        self.assertTrue(0 <= self.seg.rates['RECV'])
        self.assertTrue(0 <= self.seg.rates['SENT'])

    def test_promise(self):
        self.assertIsNone(self.seg.cargo.percentage)
        self.seg.set_percentage()
        if self.seg.promise == 0:
            self.assertIsNone(self.seg.cargo.percentage)
        else:
            self.assertIsNotNone(self.seg.cargo.percentage)

    def test_text(self):
        self.assertIsNone(self.seg.cargo.text)
        self.seg.set_text()

    def test_tooltip(self):
        self.assertIsNone(self.seg.cargo.tooltip.table)
        self.seg.set_tooltip()
        self.assertIsNotNone(self.seg.cargo.tooltip.table)

    def test_class(self):
        self.assertIsNone(self.seg.cargo.class_)
        self.seg.set_percentage()
        self.seg.set_class()
        self.assertIsNotNone(self.seg.cargo.class_)
