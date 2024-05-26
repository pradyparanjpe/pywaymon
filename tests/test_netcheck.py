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
"""Test network module"""

import unittest

from pywaymon.netcheck import NetState


class TestNetcheck(unittest.TestCase):

    def setUp(self):
        self.seg = NetState()

    def test_setup(self):
        self.assertEqual(self.seg.cargo.tooltip.title, 'Network')

    def test_clean(self):
        self.seg.get_values()

    def test_ip(self):
        del self.seg.ip_addr
        self.assertIsNotNone(self.seg.ip_addr)

    def test_gateway(self):
        del self.seg.gateway
        self.assertIsNotNone(self.seg.gateway)

    def test_apmac(self):
        del self.seg.ap_mac
        self.seg.ap_mac

    def test_buddy(self):
        del self.seg.buddy
        self.assertIsNotNone(self.seg.buddy)

    def test_zone(self):
        del self.seg.zone
        self.assertIsNotNone(self.seg.zone)

    def test_class(self):
        self.seg.set_class()
        assert self.seg.cargo.class_
        self.assertIn(self.seg.zone, self.seg.cargo.class_)
        self.assertIn(self.seg.buddy, self.seg.cargo.class_)

    def test_text(self):
        self.seg.set_text()
        self.assertIn(self.seg.icon, self.seg.cargo.text)

    def test_tooltip(self):
        self.seg.set_tooltip()
        self.assertIsNotNone(self.seg.cargo.tooltip)
