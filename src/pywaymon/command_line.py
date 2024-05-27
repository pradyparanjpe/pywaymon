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
"""Command line parser for waybar modules."""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from typing import Any, Dict


def _cli():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='''Custom python modules for waybar.''')
    comm = parser.add_mutually_exclusive_group()
    comm.add_argument('-r',
                      '--refresh',
                      action='store_true',
                      help='trigger manually')
    comm.add_argument('-p',
                      '--push-tip',
                      type=int,
                      default=0,
                      help='write (1=next, -1=prev) tip type to state file')
    parser.add_argument(
        '-i',
        '--interval',
        metavar='SEC',
        default=None,
        type=float,
        help='Trigger every SEC. "0": call only once and return exit.')
    parser.add_argument('-c',
                        '--show-config',
                        dest='show',
                        action='store_true',
                        help='show configuration for the module.')
    parser.add_argument('-t',
                        '--tip-type',
                        metavar='TYPE',
                        type=str,
                        help='start with this tip type')
    modules = parser.add_subparsers(title='Module',
                                    required=True,
                                    dest='module',
                                    help='''Waybar module segment''')
    modules.add_parser('memory', help='Memory stats')
    modules.add_parser('processor', help='CPU stats')
    modules.add_parser('temperature', help='Temperature sensors')
    modules.add_parser('load', help='CPU load')
    modules.add_parser('IO', help='I/O load')
    netio = modules.add_parser('netio', help='Networking stats')
    netio.add_argument('-P',
                       '--promise',
                       metavar='B/s',
                       type=int,
                       default=0,
                       help='Promised Speed in bytes/s (0: unknown)')
    modules.add_parser('netcheck', help='Network status')
    modules.add_parser('distro', help='System updates')
    return parser


def cli() -> Dict[str, Any]:
    return vars(_cli().parse_args())
