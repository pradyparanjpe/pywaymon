.. _usage:

######
USAGE
######

.. _SYNOPSIS:

*********
SYNOPSIS
*********

.. argparse::
   :ref: pywaymon.command_line._cli
   :prog: pywaymon

***************
Custom modules
***************

Each custom module can be called from the command line with a sub-command argument as indicated :ref:`above<SYNOPSIS>`.

Modules may have various pre-formatted tooltips as indicated (if available) in their respective sections.
The initial type of tooltip may be supplied using the tip-type argument ``-t``.
Unless supplied, the configured tip-type is used.
If unconfigured, standard tip-type is used.

.. _daemon_call:

Daemon
=======

If called with the interval argument ``-i``, *pywaymon* enters an infinite loop emitting output with an interval of supplied seconds.
We shall refer to such an instance as the `daemon` mode.
If not called with an ``-i`` argument, *pywaymon* defaults to the configured value, else emits only one test output and exits.
If value supplied with ``-i`` is ``0``, *pywaymon* does not enter daemon mode even if `configured <CONFIGURATION.html#loop-interval>`__; instead, emits only one test output and exits.

Comm
=====
While a `daemon` instance of any module is running in a loop, another `comm` instance may be called to manage the daemon.
Following arguments **imply** *comm* mode.

*pywaymon* called with refresh argument ``-r`` sends a *refresh* instruction to manually update the module before it's time.

*pywaymon* called with push argument ``-p`` with an integer value pushes the tip state in forward direction if value is positive or in reverse direction if value is negative.

.. warning::

    *pywaymon* **may not** be called with ``-i`` argument in comm mode.

.. _MODULES:

Modules
=======

Following custom modules for waybar are defined.

IO
---
- Monitors disk Input/Output wait times.

tip types
^^^^^^^^^^
- combined: disks + pids [default]
- pids: top consumer processes
- disks: disk IO

processor
----------
- Monitors CPU usage.

tip types
^^^^^^^^^^
- combined: processors + pids [default]
- pids: top consumer processes
- processors: resolved core usage


temperature
------------
- Monitors various sensors for temperature

.. seealso::
   `lmsensors <https://github.com/lm-sensors/lm-sensors>`__

memory
-------
- Monitors RAM usage.

tip types
^^^^^^^^^^
- combined: device + pids [default]
- pids: top consumer processes
- device: RAM, SWAP

netio
------
- Monitors incomming and outgoing networking data.

netcheck
---------
- Check and classify type of network.
- When IP(v4) address of host machine starts with ``192.168``, it is hidden.

.. table:: Displayed Icons

     ============ ====
     PLACE        ICON
     ============ ====
     Disconnected ❌
     Home         🏠
     Work         🛠
     Hotspot      📱
     Unknown      👽
     ============ ====

Environment Variables
^^^^^^^^^^^^^^^^^^^^^^
Following variables must be set either as Environment variables in the profile [or <planned> in *pywaymon*\ 's configuration file].

- ``internet_ip``: an IP known to respond to ping, located outside the intranet.
- ``home_ap``: a list of IP known to respond to ping, located `at home`.
- ``work_ap``: a list of IP known to respond to ping, located `at work`, but not at home.
- ``hotspot_ap``: a list of IP known to respond to ping when connected to hotspot.

distro
-------
Distribution updates monitor.

Supported
^^^^^^^^^^

- dnf
- flatpak

<Planned>
^^^^^^^^^^
- apt
- zypper
- apk
- pacman
- snap
- appimages

load
-----
System load.
1, 5, 15

**************
WayBar config
**************

Add *pywaymon* modules as 'custom/<module>' to waybar configuration based on following sample config.

Configuration
==============

.. code-block:: json
   :caption: .config/waybar/config.json

    "custom/cpu": {
        "restart-interval": 5,
        "return-type": "json",
        "exec": "pywaymon -i 5 cpu",
        "on-click": "pywaymon -r cpu",
        "on-scroll-up": "pywaymon -p -1 cpu",
        "on-scroll-down": "pywaymon -p 1 cpu",
      }

