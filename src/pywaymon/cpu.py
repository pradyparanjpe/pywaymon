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
CPU stats for waybar.

Model: ``top``
"""

from functools import reduce

import psutil

from pywaymon.base import CONFIG, KernelStats, WayBarToolTip


class CPUStats(KernelStats):
    """
    CPU statistics monitor.

    Handle that can monitor emit CPU statistics in waybar JSON format.
    """
    tip_opts = 'processors + pids', 'pids', 'processors'
    mon_name = 'processor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._core_tip = WayBarToolTip(title=self.mon_name.capitalize(),
                                       col_names=['CORE', 'LOAD'])
        self._proc_tip = WayBarToolTip(title=self.mon_name.capitalize(),
                                       col_names=['PID', 'USAGE%', 'COMMAND'])

    @property
    def proc_tip(self) -> WayBarToolTip:
        """List most 'expensive' processes."""
        hogs = (proc.info for proc in sorted(
            psutil.process_iter(['cpu_percent', 'pid', 'name']),
            reverse=True,
            key=lambda x: x.info['cpu_percent']))
        max_row = CONFIG.get('row')
        max_col = CONFIG.get('col')
        self._proc_tip.table = [[
            str(info['pid']),
            str(info['cpu_percent']), info['name']
        ][:max_col] for info in hogs][:max_row]
        return self._proc_tip

    @property
    def core_tip(self) -> WayBarToolTip:
        """Logical Core Resulution"""
        max_row = CONFIG.get('row')
        max_col = CONFIG.get('col')
        self._core_tip.table = [
            [f'{num: >2d}', f'{load:0.2f}'][:max_col]
            for num, load in enumerate(psutil.cpu_percent(percpu=True), 1)
        ][:max_row]
        return self._core_tip

    def set_percentage(self):
        self.cargo.percentage = int(psutil.cpu_percent())

    def set_class(self):
        self.cargo.class_ = 'cpu'
        if self.cargo.percentage and float(self.cargo.percentage) > 75:
            self.cargo.class_ = "full"

    def set_text(self):
        icon = '\uD83E\uDD2F' if (
            self.cargo.percentage and
            (float(self.cargo.percentage) > 75)) else '\uD83E\uDDE0'
        self.cargo.text = f'{icon} {self.cargo.percentage}%'

    def set_tooltip(self):
        """Set tooltip for waybar return"""
        tip_form = {'pids': self.proc_tip, 'processors': self.core_tip}
        self.cargo.tooltip = reduce(lambda x, y: x + tip_form.get(y),
                                    self.tip_type, WayBarToolTip())
