#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

# Copyright © 2022, 2023 Pradyumna Paranjape

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
"""
NetIO stats for waybar.

Model: ``nload``.
"""

from time import time
from typing import Dict, Optional, Tuple

import psutil

from pywaymon.base import KernelStats, WayBarToolTip, pref_unit, val_pref


class NetIOStats(KernelStats):
    """
    NetIO statistics monitor.

    Handle that can monitor emit Network IO statistics in waybar JSON format.

    Parameters
    ----------
    promise : int
        speed in Bytes Per Second as promised by ISP (divide bits into 8)
    *args : Any
        passed to :class:`KernelStats`
    **kwargs : Dict[str, Any]
        passed to :class:`KernelStats`
    """
    mon_name = 'netio'

    def __init__(self, promise: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_io: Optional[Tuple[int, int]] = None
        """Number of bytes received/sent"""

        self._rates: Optional[Dict[str, float]] = None
        """Calculated rates from differences in 'tip type' Bytes"""

        self._last_check: Optional[float] = None
        """Time-stamp of last query"""

        self.promise: int = promise or self.config.get('promise', 0)
        """Promised speed in Bits Per Second"""

        self.cargo.tooltip = WayBarToolTip(title=self.mon_name.capitalize(),
                                           col_names=list(self.rates.keys()))

    @property
    def rates(self):
        """Calculate data transfer rates."""
        if self._rates is None:
            self._rates = {'sent': 0., 'received': 0.}
            counters = psutil.net_io_counters()
            last_check = time()
            last_io = counters.bytes_recv, counters.bytes_sent
            if self._last_check is not None:
                assert self.last_io is not None
                period = time() - self._last_check
                self._rates['received'] = (last_io[0] -
                                           self.last_io[0]) / period
                self._rates['sent'] = (last_io[1] - self.last_io[1]) / period

            # memory
            self._last_check, self.last_io = last_check, last_io
        return self._rates

    @rates.deleter
    def rates(self):
        self._rates = None

    def get_values(self):
        del self.rates

    def set_percentage(self):
        """Calculate fraction of promised rate being currently used."""
        self.cargo.percentage = 0. if (not self.promise) else (
            sum(self.rates.values()) / self.promise)

    def set_text(self):
        raw_vals = sum(self.rates.values())
        if raw_vals <= self.config.get('ignore-below', 0):
            self.cargo.text = None
            return
        flux, pref = pref_unit(raw_vals)
        self.cargo.text = f'{flux} {pref}B/s'

    def set_tooltip(self):
        self.cargo.tooltip.table = [
            val_pref(value) for value in self.rates.values()
        ]

    def set_class(self):
        self.cargo.class_ = 'idle'
        if not self.cargo.percentage:
            return
        assert isinstance(self.cargo.percentage, (float, int))
        if self.cargo.percentage > 1.:
            self.cargo.class_ = 'lucky'
        elif self.cargo.percentage > 0.75:
            self.cargo.class_ = 'all'
        elif self.cargo.percentage > 0.50:
            self.cargo.class_ = 'most'
        elif self.cargo.percentage > 0.25:
            self.cargo.class_ = 'lot'
