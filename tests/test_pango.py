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

import unittest
from pathlib import Path

from pywaymon.errors import BadStyleClassError
from pywaymon.pango import PangoCssParser


class TestPango(unittest.TestCase):

    def setUp(self):
        self.pango = PangoCssParser(Path('style.css'))

    def test_err(self):
        with self.assertRaises(BadStyleClassError):
            self.pango.stylize('test_text', 'badclass')

    def test_custom(self):
        lang_tag = 'lang="en_IN.utf-8"'
        self.assertIn(lang_tag,
                      self.pango.stylize('test_text', 'custom', lang_tag))

    def test_plain(self):
        self.assertNotIn('span', self.pango.stylize('simple text'))
        self.assertNotIn('span', self.pango.stylize('test_text', 'custom'))

    def test_class(self):
        self.assertNotIn('color',
                         self.pango.stylize('some very long text', 'cell'))
        self.assertIn('span color', self.pango.stylize('test_text', 'title'))
