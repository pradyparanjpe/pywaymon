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
"""CPU tests"""

import unittest

from pywaymon.cpu import CPUStats


class TestCPU(unittest.TestCase):

    def setUp(self):
        self.seg = CPUStats()

    def test_proc_tip(self):
        self.assertEqual(self.seg.proc_tip.title, 'Processor')
        self.assertEqual(self.seg.core_tip.title, 'Processor')

    def test_text(self):
        self.seg.set_text()
        self.assertTrue(self.seg.cargo.text)

    def test_class(self):
        self.seg.set_class()
        self.assertTrue(self.seg.cargo.class_)

    def test_percent(self):
        self.seg.set_percentage()
        self.assertIsNotNone(self.seg.cargo.percentage)
        assert self.seg.cargo.percentage
        self.assertTrue(0 <= float(self.seg.cargo.percentage) <= 100)

    def test_processes(self):
        del self.seg.proc_tip.table
        self.assertIsNone(self.seg._proc_tip.table)
        # self.seg.processes()
        self.assertIsNotNone(self.seg.proc_tip.table)

    def test_cores(self):
        del self.seg.core_tip.table
        self.assertIsNone(self.seg._core_tip.table)
        # self.seg.cores()
        self.assertIsNotNone(self.seg.core_tip.table)

    def test_tooltip(self):
        original_tip_type = self.seg.tip_type
        self.seg.cargo.tooltip.table = None
        self.seg.register_state('pids')
        self.seg.set_tooltip()
        self.assertIsNotNone(self.seg.cargo.tooltip)
        self.seg.cargo.tooltip.table = None
        self.seg.register_state('processors')
        self.seg.set_tooltip()
        self.assertIsNotNone(self.seg.cargo.tooltip)
        self.seg.cargo.tooltip.table = None
        self.seg.register_state('combine')
        self.seg.set_tooltip()
        self.assertIsNotNone(self.seg.cargo.tooltip)
        self.seg.register_state(original_tip_type)
