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
"""Base Structure tests"""

import json
import unittest

from pywaymon.base import (KernelStats, WayBarReturnType, WayBarToolTip,
                           pref_unit, val_pref)
from pywaymon.errors import TipTypeError, UnitsError


class TestUnitPref(unittest.TestCase):

    def test_pref_unit(self):
        val, unit = pref_unit(2000)
        self.assertEqual(val, 2)
        self.assertEqual(unit, 'k')

    def test_bad_pref(self):
        with self.assertRaises(UnitsError):
            pref_unit(2000, 'w')

    def test_bad_val_pref(self):
        with self.assertRaises(UnitsError):
            pref_unit('2000 w')

    def test_val_pref(self):
        self.assertIn('k', val_pref(2000))


class TestTip(unittest.TestCase):

    def setUp(self):
        self.table = [[f'row_{row+1}, col_{col+1}' for row in range(3)]
                      for col in range(3)]
        self.tip = WayBarToolTip('text',
                                 title='title',
                                 row_names=['row 1', 'row 2', 'row 3'],
                                 col_names=['col 1', 'col 2', 'col 3'],
                                 table=self.table)

    def test_bool(self):
        self.assertFalse(WayBarToolTip())

    def test_tip(self):
        self.assertEqual(self.tip.table, self.table)

    def test_inherit(self):
        child = WayBarToolTip(self.tip)
        self.assertEqual(self.tip, child)
        child.table = [1, 2, 3]
        self.assertNotEqual(self.tip, child)
        child.col_names = [1, 2, 3]
        self.assertNotEqual(self.tip, child)
        child.row_names = [1, 2, 3]
        self.assertNotEqual(self.tip, child)
        child.text = 'TEXT'
        self.assertNotEqual(self.tip, child)
        child.title = 'TITLE'
        self.assertNotEqual(self.tip, child)
        self.assertNotEqual(self.tip, [1, 2, 3])

    def test_setters(self):
        del self.tip.row_names
        self.assertIsNone(self.tip.row_names)
        self.tip.row_names = 'row_1'
        self.assertEqual(self.tip.row_names, ['row_1'])
        self.tip.row_names = None
        self.assertIsNone(self.tip.row_names)

        del self.tip.col_names
        self.assertIsNone(self.tip.col_names)
        self.tip.col_names = 'col_1'
        self.assertEqual(self.tip.col_names, ['col_1'])
        self.tip.col_names = None
        self.assertIsNone(self.tip.col_names)

        del self.tip.table
        self.assertIsNone(self.tip.table)
        self.tip.table = [[1, 2, 3], [4, 5, 6]]
        self.assertEqual(self.tip.table, [['1', '2', '3'], ['4', '5', '6']])
        self.tip.table = None
        self.assertIsNone(self.tip.table)
        self.tip.table = [1, 2, 3]
        self.assertEqual(self.tip.table, [['1', '2', '3']])

    def test_combine(self):
        child_tip = WayBarToolTip(self.tip)
        # del child_tip.row_names
        combined_tip = self.tip + child_tip
        self.assertEqual(self.tip.row_names, combined_tip.row_names)
        self.assertEqual(self.tip.title, combined_tip.title)
        del child_tip.table
        combined_tip = self.tip + child_tip
        self.assertEqual(self.tip.table, combined_tip.table)
        combined_tip = child_tip + self.tip
        self.assertEqual(self.tip.table, combined_tip.table)

    def test_transpose_table(self):
        child = WayBarToolTip(self.tip, major_axis='column')
        self.assertEqual(child.table, [col for col in zip(*self.table)])
        self.tip.transpose_table()
        self.assertEqual(self.tip.table, [col for col in zip(*self.table)])
        del self.tip.table
        self.tip.transpose_table()
        self.assertIsNone(self.tip.table)

    def test_pango(self):
        lang_tag = 'lang="en_IN.utf-8"'
        self.assertIn(lang_tag, self.tip.pango('test_text', lang_tag))
        self.assertNotIn(
            'text', self.tip.pango('some very long text', lang_tag, clip=10))
        self.assertNotIn('span', self.tip.pango('simple text'))
        self.assertIn('span color', self.tip.pango('test_text', 'title'))

    def test_repr_grid(self):
        grid = self.tip.repr_grid()
        self.assertEqual(len(grid), len(self.tip.table) + 4)
        del self.tip.row_names
        grid = self.tip.repr_grid()
        self.assertEqual(len(grid), len(self.tip.table) + 4)
        print(self.tip)


class TestReturnJSON(unittest.TestCase):

    def setUp(self):
        self.cargo = WayBarReturnType(
            'Display',
            'Alternate',
            wclass=['style-class-1', 'style-class-2'],
            percentage=50.0)

    def test_json(self):
        cargo_str = str(self.cargo)
        manual_dump = json.dumps({
            'text': 'Display',
            'alt': 'Alternate',
            'tooltip': '',
            'class': ['style-class-1', 'style-class-2'],
            'percentage': '50.0'
        })
        print(cargo_str)
        print(manual_dump)
        self.assertEqual(cargo_str, manual_dump)


class TestBase(unittest.TestCase):

    def setUp(self):
        self.seg = KernelStats()

    def test_call(self):
        self.seg()

    def test_bad_tip_type(self):
        with self.assertRaises(TipTypeError):
            self.seg = KernelStats('bad tip type')

    def test_next_tip(self):
        print(self.seg.tip_type)
        print(self.seg.tip_opts)
        self.assertIsNone(self.seg.next_tip())
        self.assertIsNone(self.seg.next_tip(-1))
