#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

# Copyright © 2023-2024 Pradyumna Paranjape

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
"""Custom modules for waybar"""

from pywaymon.command_line import cli
from pywaymon.cpu import CPUStats
from pywaymon.diskio import IOStats
from pywaymon.distro import DistroUp
from pywaymon.heat import HeatStats
from pywaymon.load import CPULoad
from pywaymon.mem import MEMStats
from pywaymon.netcheck import NetState
from pywaymon.netio import NetIOStats


def main():
    """Entry Point"""
    cliargs = cli()
    push_tip = cliargs.pop('push_tip')
    refresh = cliargs.pop('refresh')
    module = cliargs.pop('module')
    show = cliargs.pop('show')
    mon = {
        'processor': CPUStats,
        'load': CPULoad,
        'distro': DistroUp,
        'IO': IOStats,
        'temperature': HeatStats,
        'memory': MEMStats,
        'netcheck': NetState,
        'netio': NetIOStats,
    }[module](**cliargs)
    if show:
        print('\n'.join(('Command line arguments:', str(cliargs), '')))
        return mon.show_config()
    if push_tip:
        direction = 'prev' if push_tip < 0 else 'next'
        data = mon.socket_commands.get(f'{direction} tip', 'refresh')
        return mon.comm(data)
    if refresh:
        return mon.comm('refresh')
    return mon()


if __name__ == '__main__':
    main()
