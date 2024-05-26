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
Disk IO stats for waybar.

Model: ``iostat``
"""

from functools import reduce
from time import time

import psutil

from pywaymon.base import CONFIG, KernelStats, WayBarToolTip, val_pref


class IOStats(KernelStats):
    """
    Disk/Process IO statistics monitor.

    Handle that can monitor emit Disk statistics in waybar JSON format.
    """
    tip_opts = 'disks + pids', 'pids', 'disks'
    mon_name = 'IO'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._proc_tip = WayBarToolTip(title=self.mon_name + ': Processes',
                                       col_names=('PID', 'B/s', 'COMMAND'))
        self._disk_tip = WayBarToolTip(title=self.mon_name + ': Disks B/s',
                                       col_names=('read', 'write'))
        self._hogs_mem = {}
        """Hold last memory of hogs"""

        self._hog_mult = ''
        """Units multiple"""

        self._disk_mem = {}
        """Hold last memory of disks IO"""

        self.disk_mult = ''
        """Disk units multiple"""

        self._time = time()
        """Hold a memory of hogs uptil now"""

    def tip_overview(self):
        """Logical disk input/outputs"""
        return ' '.join([
            f'{typ}:{val}%'
            for typ, val in psutil.cpu_times_percent()._asdict().items() if val
        ])

    @property
    def proc_tip(self):
        """ List most 'expensive' processes."""
        hogs = {
            proc.info['pid']: {
                'name':
                proc.info['name'],
                'bytes': (proc.info['io_counters'].write_bytes +
                          proc.info['io_counters'].read_bytes)
            }
            for proc in psutil.process_iter(['io_counters', 'pid', 'name'])
            if proc.info.get('io_counters')
        }

        delta_t = time() - self._time

        rate = {
            pid: {
                'bytes':
                (vals['bytes'] - self._hogs_mem.get(pid, {}).get('bytes', 0)) /
                delta_t,
                'name':
                vals['name']
            }
            for pid, vals in hogs.items()
        }

        max_row = CONFIG.get('row')
        self._proc_tip.table = [
            (str(pid), val_pref(vals['bytes']), vals['name'])
            for pid, vals in sorted(
                rate.items(), reverse=True, key=lambda x: x[1]['bytes'])
        ][:max_row]

        self._hogs_mem = hogs
        return self._proc_tip

    @property
    def disk_tip(self):
        diskio = {
            disk: io._asdict()
            for disk, io in psutil.disk_io_counters(perdisk=True,
                                                    nowrap=True).items()
        }
        self._disk_tip.row_names = list(diskio.keys())
        delta_t = time() - self._time
        delta = {
            name: [
                val_pref(
                    ((diskio.get(name, {}).get('read_count', 0) -
                      self._disk_mem.get(name, {}).get('read_count', 0))) /
                    delta_t),
                val_pref((diskio.get(name, {}).get('write_count', 0) -
                          self._disk_mem.get(name, {}).get('write_count', 0)) /
                         delta_t)
            ]
            for name, io in diskio.items()
        }
        self._disk_mem = diskio
        max_row = CONFIG.get('row')
        self._disk_tip.table = [disk for disk in delta.values()][:max_row]
        return self._disk_tip

    def set_percentage(self):
        self.cargo.percentage = int(psutil.cpu_times_percent().iowait)

    def set_text(self):
        icon = '\uD83D\uDD85' if (
            self.cargo.percentage and
            (float(self.cargo.percentage) > 50)) else '\uD83D\uDDB4'

        self.cargo.text = f'{icon} {self.cargo.percentage}%'

    def set_tooltip(self):
        """Set tooltip for waybar return"""
        self.cargo.tooltip.text = self.tip_overview()
        tip_form = {'pids': self.proc_tip, 'disks': self.disk_tip}
        self.cargo.tooltip = reduce(lambda x, y: x + tip_form.get(y),
                                    self.tip_type, WayBarToolTip())

    def set_class(self):
        self.cargo.class_ = 'io'
        if self.cargo.percentage and float(self.cargo.percentage) > 50:
            self.cargo.class_ = 'blocking'

    def sense(self):
        super().sense()
        self._time = time()
