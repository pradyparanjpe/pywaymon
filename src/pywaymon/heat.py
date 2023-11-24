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
Monitor Temperature sensors.

Model: ``sensors``
"""

from typing import Dict, Optional, Tuple

import psutil

from pywaymon.base import KernelStats, WayBarToolTip


class HeatStats(KernelStats):
    """
    Heatory statistics monitor.

    Handle that can monitor emit heatory statistics in waybar JSON format.
    """
    mon_name = 'temperature'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cargo.tooltip = WayBarToolTip(title=self.mon_name.capitalize())

        self._temp: Dict[str, Dict[str, int]] = {}
        """Current temperatures for all sensors."""

        self._alarms: Dict[str, Dict[str, int]] = {}
        """Alarming temperatures for all sensors."""

        self._coretemp: Optional[Tuple[int, int]] = None
        """Summary Temperature. Tuple: (current, alarm@)"""

    @property
    def icon(self):
        if not isinstance(self.cargo.class_, str):
            return '\uf2cb'
        return {
            'fire': '\ud83d\udd25',
            'red': '\uf2c7',
            'orange': '\uf2c8',
            'hot': '\uf2c9',
            'warm': '\uf2ca',
            'default': '\uf2cb',
        }.get(self.cargo.class_, '\uf2cb')

    @property
    def temp(self) -> Dict[str, Dict[str, int]]:
        """Query current temperatures for all sensors."""
        if not self._temp:
            self._temp = {
                dev: {
                    str(subdev.label): int(subdev.current)
                    for subdev in dat
                }
                for dev, dat in psutil.sensors_temperatures().items()
            }
        return self._temp

    @temp.deleter
    def temp(self):
        self._temp = {}

    @property
    def alarms(self) -> Dict[str, Dict[str, int]]:
        """Alarming temperatures as declared by sensor or 84."""
        if not self._alarms:
            self._alarms = {
                dev: {
                    str(subdev.label): int(getattr(subdev, 'high', 84) or 84)
                    for subdev in dat
                }
                for dev, dat in psutil.sensors_temperatures().items()
            }
        return self._alarms

    @property
    def coretemp(self) -> Optional[Tuple[int, int]]:
        """
        Pick Core temperature (of interest) from all sensors.

        Returns
        -------
        int, int
            current temperature of interest,
            Corresponding 'High' alarm at
        """
        if self._coretemp is None:
            if (core := self.temp.get('coretemp', {})):
                # first subdevice that doesn't have 'core' in label, else first label

                pack = ([
                    lab for lab in core.keys() if ('core' not in lab.lower())
                ] or list(core.keys()))
                self._coretemp = int(core[pack[0]]), self.alarms.get(
                    'coretemp', {}).get(pack[0], 84)
        return self._coretemp

    @coretemp.deleter
    def coretemp(self):
        self._coretemp = None

    def get_values(self):
        del self.temp
        del self.coretemp

    def set_percentage(self):
        r"""
        Fraction of alarming sensor heat tolerance.

        .. math::

            \frac{current - ambient}{alarm - ambient}

        scaled to percentage.
        """
        if self.coretemp is None:
            self.cargo.percentage = None
            return
        coretemp, alarmtemp = self.coretemp
        ambient = self.config['ambient']
        self.cargo.percentage = (100 * (coretemp - ambient) /
                                 (alarmtemp - ambient))

    def set_class(self):
        self.cargo.class_ = 'default'
        classifier = float(self.cargo.percentage or 0) * 0.06
        if classifier > 5:
            self.cargo.class_ = 'fire'
        elif classifier > 4:
            self.cargo.class_ = 'red'
        elif classifier > 3:
            self.cargo.class_ = 'orange'
        elif classifier > 2:
            self.cargo.class_ = 'hot'
        elif classifier > 1:
            self.cargo.class_ = 'warm'

    def set_text(self):
        self.set_class()
        self.cargo.text = (None if (self.coretemp is None) else
                           f'{self.icon} {self.coretemp[0]}\u2103')

    def set_tooltip(self):
        if not self.temp:  # pragma: no cover
            return
        if not self.cargo.tooltip.col_names:
            self.cargo.tooltip.col_names = list(self.alarms.keys())
        self.cargo.tooltip.table = [[
            ((f'{label}: ' if label else '') + f'{subtemp}\u2103')
            for label, subtemp in temp.items()
        ] for temp in self.temp.values()]
        self.cargo.tooltip.transpose_table()
