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
Distro updates

Uses: ``dnf``, ``flatpak``
"""

import platform
import subprocess
from functools import reduce

from pywaymon.base import KernelStats, WayBarToolTip


class DistroUp(KernelStats):
    mon_name = 'distro'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.distro = platform.uname().release.split('.')[-2]
        self.cargo.text = f'\uD83D\uDC27 {self.distro}'
        self.cargo.tooltip = WayBarToolTip()

    def check_dnf_updates(self):  # pragma: no cover
        updates = subprocess.run(['sudo', 'dnf', 'check-update'],
                                 text=True,
                                 stdout=subprocess.PIPE).stdout
        return len(
            [line for line in updates.split('\n') if self.distro in line])

    def check_flatpak_updates(self):  # pragma: no cover
        get_remotes = subprocess.run(['flatpak', 'remotes'],
                                     text=True,
                                     stdout=subprocess.PIPE).stdout
        fp_remotes = [
            remote.split('\t')[0]
            for remote in get_remotes.rstrip().split('\n')
        ]
        return reduce(
            lambda x, y: x + subprocess.run(
                ['flatpak', 'remote-ls', '--updates', y],
                text=True,
                stdout=subprocess.PIPE).stdout.count('\n'), fp_remotes, 0)

    def set_tooltip(self):  # pragma: no cover
        dnf_updates = self.check_dnf_updates()
        flatpak_updates = self.check_flatpak_updates()

        if dnf_updates + flatpak_updates:
            self.cargo.tooltip.title = 'Available'
            self.cargo.tooltip.col_names = ['ALL', 'DNF', 'FLATPAK']
            self.cargo.tooltip.table = [
                dnf_updates + flatpak_updates, dnf_updates, flatpak_updates
            ]
        else:
            self.cargo.tooltip.title = 'UP TO DATE'
