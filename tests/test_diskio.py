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
"""IO tests"""

import unittest

from pywaymon.diskio import IOStats


class TestIO(unittest.TestCase):

    def setUp(self):
        self.seg = IOStats()

    def test_proc_tip(self):
        self.assertEqual(self.seg.proc_tip.title, 'IO: Processes')
        self.assertEqual(self.seg.disk_tip.title, 'IO: Disks B/s')

    def test_percent(self):
        self.seg.set_percentage()
        self.assertIsNotNone(self.seg.cargo.percentage)
        assert self.seg.cargo.percentage is not None
        self.assertTrue(0 <= float(self.seg.cargo.percentage) <= 100)

    def test_processes(self):
        del self.seg.proc_tip.table
        self.assertIsNone(self.seg._proc_tip.table)
        # self.seg.processes()
        self.assertIsNotNone(self.seg.proc_tip.table)

    def test_disks(self):
        del self.seg.disk_tip.table
        self.assertIsNone(self.seg._disk_tip.table)
        # self.seg.disks()
        self.assertIsNotNone(self.seg.disk_tip.table)

    def test_tooltip(self):
        # self.seg.cargo.tooltip = None
        self.seg.set_tooltip()
        self.assertIsNotNone(self.seg.cargo.tooltip)

    def test_sense(self):
        self.seg.sense()
        self.assertTrue(self.seg.cargo)
