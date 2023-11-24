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
CPU Load average for waybar.

Model: ``uptime``
"""

from typing import Optional, Tuple

import psutil

from pywaymon.base import KernelStats, WayBarToolTip


class CPULoad(KernelStats):
    """
    CPU Loads monitor.

    Handle that can monitor emit CPU Load averages in waybar JSON format.
    """
    mon_name = 'load'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loads: Optional[Tuple[float, ...]] = None
        self.cargo.tooltip = WayBarToolTip(title=self.mon_name.capitalize(),
                                           col_names=('1 min', '5 min',
                                                      '15 min'))

    @property
    def loads(self):
        """Processor loads"""
        if self._loads is None:
            self._loads = tuple(round(load, 2) for load in psutil.getloadavg())
        return self._loads

    @loads.deleter
    def loads(self):
        self._loads = None

    def get_values(self):
        del self.loads

    def set_text(self):
        self.cargo.text = (None if (self.loads is None
                                    or self.cargo.class_ == 'unloaded') else
                           ('\uD83C\uDFCB' + ' '.join(
                               (str(load) for load in self.loads))))

    def set_class(self):
        """
        Set waybar style class.

        Indicates why we consider the processor loaded.

        Values
        ------

        - unloaded : Processor is unloaded
        - 1 min : 1 minute load is greater that (2 * nproc)
        - 5 min : 5 minute load is greater that (1.5 * nproc)
        - 15 min : 15 minute load is greater that (nproc)

        """
        self.cargo.class_ = 'unloaded'
        if self.loads is None:
            return
        nprocs = psutil.cpu_count() or 1
        if self.loads[0] > (2 * nprocs):
            self.cargo.class_ = '1 min'
        elif self.loads[1] > (1.5 * nprocs):
            self.cargo.class_ = '5 min'
        elif self.loads[2] > (1 * nprocs):
            self.cargo.class_ = '15 min'

    def set_tooltip(self):
        self.cargo.tooltip.table = self.loads
