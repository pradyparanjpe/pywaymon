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
Identify network connections and type.

Uses: ``ping``, ``arp``
"""

import os
import socket
import struct
import subprocess
from typing import Optional

from pywaymon.base import KernelStats, WayBarToolTip


class NetState(KernelStats):
    mon_name = 'netcheck'

    def __init__(self, *args, **kwargs):
        """Current IP address"""
        super().__init__(*args, **kwargs)
        self._ip_addr: Optional[str] = None
        self._ap_mac: Optional[str] = None
        self._gateway: Optional[str] = None
        self._buddy: Optional[str] = None
        self._zone: Optional[str] = None
        self.cargo.tooltip = WayBarToolTip(title='Network')

    @property
    def icon(self):
        """Icons indicating (un)known networks."""
        return {
            'disconnected': '\u274C',
            'alien': '\uD83D\uDC7D',
            'home': '\uD83C\uDFE0',
            'work': '\uD83D\uDEE0',
            'hotspot': '\uD83D\uDCF1'
        }.get(self.buddy, '\uD83D\uDC7D')

    @property
    def ip_addr(self) -> str:
        if self._ip_addr is None:
            self._ip_addr = socket.gethostbyname(socket.gethostname())
        return self._ip_addr

    @ip_addr.deleter
    def ip_addr(self):
        self._ip_addr = None

    @property
    def gateway(self) -> str:
        """Access point (default gateway)"""
        if self._gateway is None:
            self._gateway = 'Unknown'
            with open('/proc/net/route') as route_fh:
                for line in route_fh:
                    fields = line.strip().rstrip().split()
                    if (fields[1] == '00000000') and (int(fields[3], 16) & 2):
                        self._gateway = socket.inet_ntoa(
                            struct.pack('<L', int(fields[2], 16)))
                        break
        return self._gateway

    @gateway.deleter
    def gateway(self):
        self._gateway = None

    @property
    def ap_mac(self) -> Optional[str]:
        """MAC of Access point (default gateway)"""
        if self._ap_mac is None:
            with open('/proc/net/arp') as arp_fh:
                for line in arp_fh:
                    fields = line.strip().rstrip().split()
                    if fields[0] == self.gateway:
                        self._ap_mac = fields[3]
        return self._ap_mac

    @ap_mac.deleter
    def ap_mac(self):
        self._ap_mac = None

    @property
    def buddy(self) -> str:
        r"""
        Are we at home/work/roaming with a hotspot?

        If ping to any of the IPs listed in the corresponding
        environment-variable is successful, return that buddy.

        Environment Variables
        ---------------------
        - ``$home_aps``\ ="HOME_AP1 HOME_AP2 HOME_AP3 ..."
        - ``$work_aps``\ ="WORK_AP1 WORK_AP2 WORK_AP3 ..."
        - ``$hotspot_aps``\ ="HOTSPOT_AP1 HOTSPOT_AP2 HOTSPOT_AP3 ..."
        - ``$home_macs``\ ="HOME_MAC1 HOME_MAC2 HOME_MAC3 ..."
        - ``$work_macs``\ ="WORK_MAC1 WORK_MAC2 WORK_MAC3 ..."
        - ``$hotspot_macs``\ ="HOTSPOT_MAC1 HOTSPOT_MAC2 HOTSPOT_MAC3 ..."

        """
        if self._buddy is None:
            self._buddy = 'alien'
            for known in 'home', 'work', 'hotspot':
                for idtt in 'ap', 'mac':
                    # TODO: What about mac?
                    if any(
                        (self.ping_target(known_ap) for known_ap in os.getenv(
                            f'{known}_{idtt}', '').split())):
                        self._buddy = known
                        break
        return self._buddy

    @buddy.setter
    def buddy(self, value: str):
        self._buddy = value

    @buddy.deleter
    def buddy(self):
        self._buddy = None

    @property
    def zone(self) -> str:
        """
        Check network connection.

        Check network by pinging destinations on the inter-, intranet.

        Returns
        -------
        str
            connected network type
        """
        if self.ip_addr is None or (self.ip_addr[:7] == '127.0.0'):
            return 'alone'
        if self.ping_target(self.config['internet']):
            return 'inter'
        if (self.gateway != 'Unknown') and self.ping_target(self.gateway):
            return 'intra'
        return 'alone'

    @zone.deleter
    def zone(self):
        self._zone = None

    @staticmethod
    def ping_target(ip_addr: str) -> bool:
        """
        Ping target to check if reachable (and responsive).

        Parameters
        ----------
        ip_addr : str
            target ip address to ping

        Returns
        -------
        bool
            reachable and responsive

        """
        return subprocess.call(['ping', '-c', '1', '-q', '-w', '2', ip_addr],
                               stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE) == 0

    def get_values(self):
        del self.zone, self.buddy, self.ip_addr, self.gateway, self.ap_mac

    def set_text(self):
        self.cargo.text = self.icon + ' ' + (self.ip_addr[8:] if
                                             (self.ip_addr[:8]
                                              == '192.168.') else self.ip_addr)

    def set_class(self):
        self.cargo.class_ = [self.zone, self.buddy]

    def set_tooltip(self):
        if self.zone == 'alone':
            self.buddy = 'disconnected'
            self.cargo.tooltip.text = 'Network disconnected'
        else:
            self.cargo.tooltip.row_names = [self.buddy, 'IP', 'GATEWAY']
            self.cargo.tooltip.table = [
                f'{self.zone}net', self.ip_addr, self.gateway
            ]
            self.cargo.tooltip.transpose_table()
