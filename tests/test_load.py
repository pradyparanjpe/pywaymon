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
"""Test distro updates segment"""

import unittest

from pywaymon.load import CPULoad


class TestLoad(unittest.TestCase):

    def setUp(self):
        self.seg = CPULoad()

    def test_setup(self):
        self.assertEqual(self.seg.cargo.tooltip.title, 'Load')

    def test_load(self):
        self.assertIsNotNone(self.seg.loads)

    def test_text(self):
        self.seg.set_text()
        self.assertTrue(self.seg.cargo.text)

    def test_tooltip(self):
        self.assertIsNone(self.seg.cargo.tooltip.table)
        self.seg.set_tooltip()
        self.assertIsNotNone(self.seg.cargo.tooltip.table)

    def test_get_values(self):
        self.seg.get_values()
        self.assertIsNone(self.seg._loads)

    def test_class(self):
        self.assertIsNone(self.seg.cargo.class_)
        self.seg.set_class()
        self.assertIsNotNone(self.seg.cargo.class_)
