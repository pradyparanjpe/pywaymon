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
CPU stats for waybar.

Model: ``top``
"""

import psutil

from pywaymon.base import KernelStats, WayBarToolTip


class CPUStats(KernelStats):
    """
    CPU statistics monitor.

    Handle that can monitor emit CPU statistics in waybar JSON format.
    """
    tip_types = 'combined', 'pids', 'processors'
    mon_name = 'processor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.core_tip = WayBarToolTip(title=self.mon_name.capitalize(),
                                      col_names=['CORE', 'LOAD'])
        self.proc_tip = WayBarToolTip(title=self.mon_name.capitalize(),
                                      col_names=['PID', 'USAGE%', 'COMMAND'])

    def processes(self):
        """List most 'expensive' processes."""
        hogs = list(proc.info for proc in sorted(
            psutil.process_iter(['cpu_percent', 'pid', 'name']),
            reverse=True,
            key=lambda x: x.info['cpu_percent']))
        self.proc_tip.table = [[
            str(info['pid']),
            str(info['cpu_percent']), info['name']
        ] for info in hogs]

    def cores(self):
        """Logical Core Resulution"""
        self.core_tip.table = [[
            f'{num: >2d}', f'{load:0.2f}'
        ] for num, load in enumerate(psutil.cpu_percent(percpu=True), 1)]

    def set_percentage(self):
        """Set percentage of waybar return"""
        self.cargo.percentage = int(psutil.cpu_percent())

    def set_tooltip(self):
        """Set tooltip for waybar return"""
        if self.tip_type == 'pids':
            self.processes()
            self.cargo.tooltip = self.proc_tip
        elif self.tip_type == 'processors':
            self.cores()
            self.cargo.tooltip = self.core_tip
        else:
            self.cores()
            self.processes()
            self.cargo.tooltip = self.core_tip + self.proc_tip

    def set_class(self):
        self.cargo.class_ = 'cpu'
        if self.cargo.percentage and float(self.cargo.percentage) > 75:
            self.cargo.class_ = "full"

    def set_text(self):
        icon = '\uD83E\uDD2F' if (
            self.cargo.percentage and
            (float(self.cargo.percentage) > 75)) else '\uD83E\uDDE0'
        self.cargo.text = f'{icon} {self.cargo.percentage}%'
