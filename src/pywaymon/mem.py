#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

# Copyright © 2022-2024 Pradyumna Paranjape

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
Memory stats for waybar.

Model: ``top``
"""

from functools import reduce

import psutil

from pywaymon.base import CONFIG, KernelStats, WayBarToolTip


class MEMStats(KernelStats):
    """
    Memory statistics monitor.

    Handle that can monitor emit memory statistics in waybar JSON format.
    """
    tip_opts = 'pids', 'device'
    mon_name = 'memory'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dev_tip = WayBarToolTip(title=self.mon_name.capitalize(),
                                      col_names=['USED', 'TOTAL'],
                                      row_names=['RAM', 'SWAP'])
        self._proc_tip = WayBarToolTip(title=self.mon_name.capitalize(),
                                       col_names=('PID', 'USAGE%', 'COMMAND'))

    @property
    def proc_tip(self) -> WayBarToolTip:
        """List most 'expensive' processes."""
        hogs = (proc.info for proc in sorted(
            psutil.process_iter(['memory_percent', 'pid', 'name']),
            reverse=True,
            key=lambda x: x.info['memory_percent']))
        max_row = CONFIG.get('row')
        max_col = CONFIG.get('col')
        self._proc_tip.table = [[
            str(info['pid']), ("%0.2f" % info['memory_percent']), info['name']
        ][:max_col] for info in hogs][:max_row]
        return self._proc_tip

    @property
    def dev_tip(self) -> WayBarToolTip:
        max_row = CONFIG.get('row')
        max_col = CONFIG.get('col')
        self._dev_tip.table = [[
            f'{dev.used / 0x40000000:0.2f}', f'{dev.total / 0x40000000:0.2f}'
        ][:max_col]
                               for dev in (psutil.virtual_memory(),
                                           psutil.swap_memory())][:max_row]
        return self._dev_tip

    def set_percentage(self):
        self.cargo.percentage = int(psutil.virtual_memory().percent)

    def set_text(self):
        icon = '\uD83D\uDD2A' if (
            self.cargo.percentage and
            (float(self.cargo.percentage) > 75)) else '\uD83D\uDC0F'
        self.cargo.text = f'{icon} {self.cargo.percentage}%'

    def set_class(self):
        self.cargo.class_ = 'mem'
        if self.cargo.percentage:
            if float(self.cargo.percentage) > 80:
                self.cargo.class_ = "filled"
            elif float(self.cargo.percentage) > 66:
                self.cargo.class_ = "filling"
            elif float(self.cargo.percentage) > 50:
                self.cargo.class_ = "warn"

    def set_tooltip(self):
        """Set tooltip for waybar return"""
        tip_form = {'pids': self.proc_tip, 'device': self.dev_tip}
        self.cargo.tooltip = reduce(lambda x, y: x + tip_form.get(y),
                                    self.tip_type, WayBarToolTip())
