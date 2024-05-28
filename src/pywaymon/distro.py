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
Distro updates.

Uses: ``apk``, ``apt``, ``dnf``, ``pacman``, ``zypper``, ``flatpak``, ``snap``,
whichever available.
"""

import platform
import shutil
import subprocess
from functools import reduce
from typing import Dict, List

from pywaymon.base import KernelStats, WayBarToolTip

MANAGERS: Dict[str, List[str]] = {
    'apk': ['apk', '-u', 'list'],
    'apt': ['apt', 'list', '--upgradable'],
    'dnf': ['sudo', 'dnf', 'check-update'],
    'pacman': ['pacman', '-Qu'],
    'zypper': ['zypper', 'list-updates'],
    'flatpak': ['flatpak', 'remote-ls', '--updates', 'args'],
    'snap': ['sudo', 'snap', 'refresh', '--list']
}
"""Package managers and command arguments to list available upgrades."""


class DistroUp(KernelStats):
    mon_name = 'distro'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.distro = platform.uname().release.split('.')[-2]
        self.cargo.text = f'\uD83D\uDC27 {self.distro}'
        self.cargo.tooltip = WayBarToolTip()

    def check_updates(self, man: str, *args:
                      str) -> List[str]:  # pragma: no cover
        """
        Check for updates for package manager.

        Parameters
        -----------
        man : str
            package manager
        *args : str
            all are inserted in place of 'args' in the command args

        Returns
        --------
        List[str]
            Output lines as list.
        """
        if not ((man in MANAGERS) and shutil.which(man)):
            return []
        cmdargs = MANAGERS[man]
        if 'args' in cmdargs:
            insert_at = cmdargs.index('args')
            cmdargs.remove('args')
            for arg in reversed(args):
                cmdargs.insert(insert_at, arg)
        return subprocess.run(
            cmdargs, text=True,
            stdout=subprocess.PIPE).stdout.strip().rstrip().split('\n')

    def check_flatpak_updates(self):  # pragma: no cover
        get_remotes = subprocess.run(
            ['flatpak', 'remotes'], text=True,
            stdout=subprocess.PIPE).stdout.rstrip().split('\n')
        """
        Flatpak remotes' updates.


        Returns
        -------
        Number of available updates
        """

        fp_remotes = [remote.split('\t')[0] for remote in get_remotes]
        return reduce(lambda x, y: x + len(self.check_updates('flatpak', y)),
                      fp_remotes, 0)

    def gather_updates(self):
        """Gather updates if available from all package managers."""
        updates = {}
        updates['apk'] = len(self.check_updates('apk'))
        updates['apt'] = max(0, len(self.check_updates('apt')))
        updates['dnf'] = len([
            line for line in self.check_updates('dnf') if self.distro in line
        ])
        updates['pacman'] = len(self.check_updates('pacman'))
        updates['zypper'] = len(self.check_updates('zypper'))
        updates['flatpak'] = self.check_flatpak_updates()
        updates['snap'] = max(0, len(self.check_updates('snap')) - 1)
        return dict(filter(lambda x: bool(x[1]), updates.items()))

    def set_tooltip(self):  # pragma: no cover
        self.cargo.tooltip.title = 'UP TO DATE'
        updates = self.gather_updates()
        if updates:
            self.cargo.tooltip.title = 'Available'
            self.cargo.tooltip.col_names = ['ALL'] + list(updates.keys())
            self.cargo.tooltip.table = [[sum(updates.values())] +
                                        list(updates.values())]
