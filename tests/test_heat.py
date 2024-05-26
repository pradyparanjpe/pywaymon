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
"""Test temperature sensor monitor module"""

import unittest

from pywaymon.heat import HeatStats


class TestHeat(unittest.TestCase):

    def setUp(self):
        self.seg = HeatStats()

    def test_setup(self):
        self.assertEqual(self.seg.cargo.tooltip.title, 'Temperature')

    def test_heat(self):
        self.assertTrue(isinstance(self.seg.temp, dict))

    def test_coretemp(self):
        if self.seg.temp:
            self.assertTrue(self.seg.coretemp[0])

    def test_get_vals(self):
        self.seg.get_values()
        self.assertFalse(self.seg._temp)
        self.assertIsNone(self.seg._coretemp)

    def test_percentage(self):
        self.seg.set_percentage()
        if self.seg.coretemp is None:
            self.assertIsNone(self.seg.cargo.percentage)
        else:
            self.assertIsNotNone(self.seg.cargo.percentage)

    def test_text(self):
        self.seg.set_text()
        if self.seg.coretemp is None:
            self.assertIsNone(self.seg.cargo.text)
        else:
            self.assertIsNotNone(self.seg.cargo.text)

    def test_tooltip(self):
        self.seg.set_tooltip()

    def test_class(self):
        self.assertIsNone(self.seg.cargo.class_)
        self.seg.set_class()
        self.assertIsNotNone(self.seg.cargo.class_)
