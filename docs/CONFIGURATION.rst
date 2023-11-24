**************
CONFIGURATION
**************

We use `XDGPSPCONF <https://pradyparanjpe.gitlab.io/xdgpspconf/index.html>`__.

Briefly, a file named ``${XDG_CONFIG_HOME:-${HOME}/.config}/pywaymon/config.yml`` may hold configuration.

Sections
=========

table
------
tooltip table format section

- color: colors understood by pango markup.
    - title: tooltip title color (**THIS IS BOLD BY DEFAULT**)
    - row_name: tooltip table row index color
    - col_name: tooltip table column index color

.. warning::
    ``#`` indicates both, hex-color and beginning of comment (in e.g. yaml format).
    Remember to quote (e.g. ``"#1f2e3d"``).

Common
---------

- For each segment, following common values may be configured.

lowest
~~~~~~~
If the value of ``lowest`` is set as a percentage between 0 and 100, the segment is displayed only if the ``percentage`` value is greater than the set value.
If not set, the segment is always shown.

tip-type
~~~~~~~~~
Type of tooltip that is displayed on mouse-hover.
For compatible tip-types, check `usage <usage.html#list>`__

Specific
---------

- Additionally, following segments accept indicated variables.


.. table ::
    :class: longtable

    ============= ============ ================================================
    Segment       Variable     Description
    ============= ============ ================================================
    netcheck      internet     A known reachable ip address located
                               in the internet, outside the intranet.
    temperature   ambient      Average ambient temperature in ℃
    netio         ignore-below Don't display value below this absolute rate.
    netio         promise      Rate promised by internet service provider (ISP)
                               in bytes/second.
    ============= ============ ================================================


.. tip::
   - ``ignore-below`` is not the same as ``lowest`` as it doesn't check for *percentage*.
   - ISPs usually promise rate in bits/second.
     ``8 bits = 1 byte``

Example
========

This is the Default.

.. tabs::

   .. tab:: yaml

      .. literalinclude:: ../src/pywaymon/config.yml
         :language: yaml
         :caption: default config

   .. tab:: toml

        .. code-block:: toml

            [table]

            [table.colors]
            title = "#ffafaf"
            row_name = "#ffffaf"
            col_name = "#afffaf"

            [table.max]
            row = 12
            word = 15

            [IO]
            lowest = 0  # recommend: 25
            tip-type = "combined"

            [processor]
            lowest = 0  # recommend: $ echo "100/$(nproc)" | bc
            tip-type = "combined"

            [temperature]
            ambient = 27  # Temperature in degrees Celcius
            lowest = 0  # This is percent of alarm temperature, not degrees Celcuis 

            [memory]
            lowest = 0   # recommend: 25
            tip-type = "combined"

            [netcheck]
            internet = 8.8.8.8  # Google's DNS as an indicator of connection to internet

            [netio]
            ignore-below = 1024  # [= 1kB/s] Ignore below this speed (bytes/s)
