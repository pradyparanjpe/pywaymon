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
"""Base Custom Module (segment)."""

import json
import os
import re
import socket
from dataclasses import dataclass
from itertools import zip_longest
from math import log2, log10
from pathlib import Path
from typing import (Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple,
                    Union)

from pywaymon.errors import TipTypeError, UnitsError
from pywaymon.pango import PangoCssParser
from pywaymon.read_config import read_config

CONFIG = read_config()
"""Super-imposed configurations."""

PANGO = PangoCssParser()
"""Stylize pango with css."""

MAX_ROW = CONFIG.get('tooltip', {}).get('max', {}).get('row')
"""Limit on table rows (from config)."""

MAX_COL = CONFIG.get('tooltip', {}).get('max', {}).get('col')
"""Limit on table columns (from config)."""

BAR = CONFIG.get('tooltip', {}).get('sep', '\u2502')
"""Separates combined tables."""

VALRE = re.compile(r'([0-9]*\.?[0-9]*) *(\w)?')
"""Regular Expression for values suffixed with standard unit prefixes."""

STD_PREF = (
    'q',  # quecto
    'r',  # ronto
    'y',  # yocto
    'z',  # zepto
    'a',  # atto
    'f',  # femto
    'p',  # pico
    'n',  # nano
    '\u03bc',  # micro
    'm',  # milli
    '',  # <base>
    'k',  # kilo
    'M',  # mega
    'G',  # giga
    'T',  # tera
    'P',  # peta
    'E',  # exa
    'Z',  # zetta
    'Y',  # yotta
    'R',  # ronna
    'Q'  # quetta
)
"""Standard unit prefixes."""


def nop(*args: Any, **kwargs: Any):
    """
    No Operation.

    Accept arbitrary number of argument and keyword arguments and do nothing.

    Parameters
    ----------
    args : Any
        all are ignored
    kwargs : Any
        all are ignored

    Returns
    -------
    None
    """


def pref_unit(val: Union[str, int, float],
              /,
              pref: str = '',
              binary: bool = True) -> Tuple[float, str]:
    """
    Represent number with standard unit prefixes.

    .. seealso::

        `metric si prefixes <https://www.nist.gov/pml/owm/metric-si-prefixes>`__

    Parameters
    ----------
    val : Union[int, float, str]
        raw value
    pref : str
        val is itself expressed with this unit prefix
    binary : bool
        Binary (i.e. powers of 2^10) units
        rather than decimal (i.e. powers of 10^3)

    Raises
    ------
    UnitsError
        Supplied unit is not standard

    Returns
    -------
    Tuple[float, str]
        Value and prefix represented in nearest standard.

    Examples
    --------
    >>> print(pref_unit('20 M', 'm'))
    (20.0, 'k')
    """
    mult = 1.
    sep_ord = 1024 if binary else 1000
    try:
        mult *= (sep_ord**(STD_PREF.index(pref or '') - 10))
    except ValueError:
        raise UnitsError(pref)

    if isinstance(val, str):
        # value supplied as string
        # may be already unit-prefixed
        if (mat := VALRE.match(val)):
            val, v_pref = mat.groups()
            try:
                mult *= (sep_ord**(STD_PREF.index(v_pref or '') - 10))
            except ValueError:
                raise UnitsError(v_pref)
    _val = float(val) * mult
    if _val == 0:
        return 0, ''
    pref_ord = int(
        min(
            max(
                round(log2(_val) // 10) if binary else round(log10(_val) // 3),
                -10), 10))
    return round(_val / (sep_ord**pref_ord), 1), STD_PREF[pref_ord + 10]


def val_pref(val: Union[int, float, str],
             /,
             pref: str = '',
             binary: bool = True,
             spacer: str = '',
             after: str = '') -> str:
    """
    Represent value as a string of suitable order and unit-prefix.

    Parameters
    ----------
    val : Union[int, float, str]
        passed to :func:`pref_unit`
    pref : str
        passed to :func:`pref_unit`
    binary : bool
        passed to :func:`pref_unit`
    spacer : str
        spacer to separate value from unit-prefix
    after : str
        spacer to separate unit-prefix from next word (unit)

    Returns
    -------
    str
        value prefix formatted as a string

    Examples
    --------
    >>> print(val_pref(20_000_000, spacer=' ') + 'B/s')
    19.1 MB/s
    """
    val, pref = pref_unit(val, pref=pref, binary=binary)
    return f'{val}{spacer}{pref}{after}'


@dataclass
class ModConf:
    """
    Base Module config.
    """
    loop_interval: float = 0.
    """Default loop interval."""
    lowest: float = 0.
    """Lowest value percent displayed below which, module segment is hidden."""
    tip_type: str = ''
    """Default hover tip-type."""


class WayBarToolTip:
    """
    Formatted Tooltip.

    Depending on availability of values, print tooltip of following types:

    - Titled Table
    - Table
    - Titled Paragraph
    - Paragraph

    .. warning::
        This is only a formatting object. Indexing like pandas is intentionally
        kept beyond scope.

    Parameters
    ----------
    text : Optional[Union[WayBarToolTip, str]]
        Plain text
    title : Optional[str]
        Title, displayed as bold, colored, underlined
    **kwargs : Dict[str, Any]
        row_names : Optional[Iterable[str]]
            row names, unavailable rows are given empty names
        col_names : Optional[Iterable[str]]
            col names, unavailable columns are given empty names
        table : Optional[Sequence[Union[Sequence[str], str]]]
            Tabular values. If lengths mismatch, the remaining are left empty
        idx_col : Optional[Sequence[int]]
            column numbers which should be formatted as index
        major_axis : {'row', 'column'}
            row : table is supplied as rows of cells (default, fallback)
            column : table is supplied as columns of cells

    """

    def __init__(self,
                 text: Optional[Union['WayBarToolTip', str]] = None,
                 *,
                 title: Optional[str] = None,
                 **kwargs):
        self.title = title
        """Tooltip title."""

        self._row_names: Optional[Iterable[Union[str, int, float]]] = None
        self._col_names: Optional[Iterable[Union[str, int, float]]] = None
        self._table: Optional[Sequence[Sequence[Union[str, int,
                                                      float]]]] = None

        # use property setters to regularize structures
        self.table = kwargs.get('table')
        self.row_names = kwargs.get('row_names')
        self.col_names = kwargs.get('col_names')

        self.idx_col: Set[int] = set(kwargs.get('idx_col', []))
        """Column numbers in table, which should be formatted as row_names."""

        if isinstance(text, WayBarToolTip):
            self.copy(text)
        else:
            self.text = text
            """Free-flowing text."""

        if self.table and (kwargs.get('major_axis', 'row') == 'column'):
            self.transpose_table()

    @property
    def row_names(self) -> Optional[List[Union[str, int, float]]]:
        """Names of rows in the table."""
        if not self._row_names:
            return None
        row_names = list(self._row_names)
        return row_names[:MAX_ROW] if MAX_ROW else row_names

    @row_names.setter
    def row_names(self, value: Optional[Union[Iterable[Union[str, int, float]],
                                              Union[str, int, float]]]):
        if value is None:
            self._row_names = None
            return
        if isinstance(value, (str, int, float)):
            self._row_names = [value]
            return
        self._row_names = value

    @row_names.deleter
    def row_names(self):
        self._row_names = None

    @property
    def col_names(self) -> Optional[List[Union[str, int, float]]]:
        """Names of columns in the table."""
        if not self._col_names:
            return None
        col_names = list(self._col_names)
        return col_names[:MAX_COL] if MAX_COL else col_names

    @col_names.setter
    def col_names(self, value: Optional[Union[Iterable[Union[str, int, float]],
                                              Union[str, int, float]]]):
        if value is None:
            self._col_names = None
            return
        if isinstance(value, (str, int, float)):
            self._col_names = [value]
            return
        self._col_names = value

    @col_names.deleter
    def col_names(self):
        self._col_names = None

    @property
    def table(self) -> Optional[Sequence[Sequence[Union[str, int, float]]]]:
        """Tooltip table."""
        return self._table[:MAX_ROW] if self._table else None

    @table.setter
    def table(self, value: Optional[Sequence[Union[Sequence[Union[str, int,
                                                                  float]],
                                                   Union[str, int, float]]]]):
        if value is None:
            self._table = None
        elif isinstance(value[0], (str, int, float)):
            # 1 Dimensional
            self._table = [[str(itm) for itm in value]]
        else:
            # 2 Dimensional
            self._table = [
                [str(itm) for itm in row]  # type: ignore [union-attr]
                for row in value
            ]

    @table.deleter
    def table(self):
        self._table = None

    def __bool__(self) -> bool:
        """
        Tooltip contains any information.

        Returns
        -------
        ``False`` if only a placeholder without any data.
        """
        if all((attr is None
                for attr in (self.title, self.text, self.row_names,
                             self.col_names, self.table))):
            return False
        return True

    def __eq__(self, other) -> bool:
        """
        Each of self's attributes match other's.

        Compared attributes
        -------------------
        - :attr:`title`
        - :attr:`~text`
        - :attr:`~row_names`
        - :attr:`~col_names`
        - :attr:`~table`
        """
        if not isinstance(other, WayBarToolTip):
            return NotImplemented
        if not self.title == other.title:
            return False
        if not self.text == other.text:
            return False
        if not self.row_names == other.row_names:
            return False
        if not self.col_names == other.col_names:
            return False
        if not self.table == other.table:
            return False
        return True

    def __str__(self) -> str:
        return '\n'.join(('\t'.join(row) for row in self.repr_grid()))

    def __add__(self, other: Optional['WayBarToolTip']) -> 'WayBarToolTip':
        """
        Combine tooltips.

        .. warning::

            ``self + other != other + self``.

        Asymmetrically add another tooltip to self.
        Attributes are combined by following rules.

        Combination Rules
        -----------------

        Title
        ~~~~~
        Use self's title if available, else use other's

        Text
        ~~~~
        self's text if available, then on the next line, other's text

        Table
        ~~~~~
        If any of the contributors lacks table, the other's is used.
        If both have tables, they are combined side-by-side.

        Rows
        ^^^^
        N\\ :sup:`th` row is constructed as:

        ``self.row_N │ other.row_N``

        This includes formatted row-names and column-names.
        Unavailable fields are replaced by tab-delimited blank strings.

        Parameters
        ----------
        other: second tooltip

        Returns
        -------
        :class:`WayBarToolTip`
            Combined tooltips
        """
        if not other:
            return self
        if not self:
            return other
        combined_idx_col: Set[int] = self.idx_col

        # simple `use A else use B` code
        combined_title = self.title if self.title else other.title
        combined_text = ((self.text or '') + '\n' +
                         (other.text or '')).strip('\n').rstrip('\n')
        combined_col_names = None
        combined_row_names = None
        combined_table = None
        combined_row_names = self.row_names
        if other.table is None:
            combined_col_names = self.col_names
            combined_table = self.table

        elif self.table is None:
            combined_col_names = other.col_names
            combined_table = other.table

        else:
            # Combination Grid
            my_cols = max(len(row) for row in self.table)

            # Column-Names
            # Self's Named Columns
            combined_col_names = self.col_names if self.col_names else []

            # Self's Blank Columns
            combined_col_names = [
                *combined_col_names,
                *([''] * (my_cols - len(combined_col_names))), BAR
            ]

            # Other's columns
            if other.row_names:
                # Place holder for top left corner of second part
                combined_col_names.append('')
                combined_idx_col.add(my_cols + 1)
                combined_idx_col |= set(col + my_cols + 1
                                        for col in other.idx_col)
            else:
                combined_idx_col |= set(col + my_cols + 1
                                        for col in other.idx_col)

            combined_col_names.extend(
                (other.col_names if other.col_names else []))

            combined_table = [
                [
                    *my_row,  # mine
                    *[''] * (my_cols - len(my_row)),  # blanks
                    BAR,  # BAR
                    *([
                        other.row_names[row_num] if
                        (len(other.row_names) > row_num) else ''
                    ] if other.row_names else []),  # its rows
                    *its_row  #its
                ] for row_num, (my_row, its_row) in enumerate(
                    zip_longest(*(self.table, other.table), fillvalue=()))
            ]
        return WayBarToolTip(title=combined_title,
                             text=combined_text,
                             col_names=combined_col_names,
                             row_names=combined_row_names,
                             table=combined_table,
                             idx_col=combined_idx_col)

    def compose(self, text: Any, class_: str, clip: int = 0) -> str:
        """
        :meth:`clip` and :meth:`pywaymon.pango.PangoCssParser.stylize`.

        Parameters
        ----------
        text : Any
            text to clip, will be converted to string form.

        class_ : str
            style class of text. Referred for configured value.

        clip : int
            Clip text to these many characters.
            Default: from CONFIG or leave intact.

        Returns
        -------
        str
            Clipped, stylized string
        """
        return PANGO.stylize(self.clip(text, class_, clip), class_)

    def clip(self, text: Any, class_: str, clip: int = 0) -> str:
        """
        Clip text to configured number of characters.

        Parameters
        ----------
        text : Any
            text to clip, will be converted to string form.

        class_ : str
            style class of text. Referred for configured value.

        clip : int
            Clip text to these many characters.
            Default: from CONFIG or leave intact.

        Returns
        -------
        str
            Clipped string
        """
        clip = clip or CONFIG['tooltip'].get('clip', {}).get(class_)
        if clip:
            return str(text)[:clip]
        return str(text)

    def repr_grid(self) -> List[List[str]]:
        r"""
        String representation of tool-tip.

        Representation order
        --------------------
        `Title` (colored, bold, underlined)
        `Text` (plain)

        .. table:: table structure

            ============== ========== ========== ==========
            \              Col Name 1 Col Name 2 Col Name 3
            ============== ========== ========== ==========
            **Row Name 1** val: 1, 1  val: 1, 2  val: 1, 3
            **Row Name 2** val: 2, 1  val: 2, 2  val: 2, 3
            **Row Name 3** val: 3, 1  val: 1, 2  val: 3, 3
            ============== ========== ========== ==========

        Row-separators: '<TAB>'.

        Missing values are left empty.
        If all values are missing, that section is dropped.

        Returns
        -------
        str
            printable representation
        """
        fmt_rep: List[List[str]] = []
        if self.title:
            fmt_rep.extend(([self.compose(self.title, 'title')], []))
        if self.text:
            fmt_rep.append([self.compose(self.text, 'text')])
        fmt_rep.extend(self.format_table())
        return fmt_rep

    def format_table(self) -> List[List[str]]:
        """
        Formatted table as list of rows.

        Each row is a list of cells (fields)
        """
        if not self.table:
            return []
        fmt_tab: List[List[str]] = []
        if self.col_names:
            fmt_tab.append(
                ([''] if self.row_names else []) +
                [self.compose(name, 'col-name') for name in self.col_names])
        # remaining column headers will remain blank anyway

        # add row names to table
        if self.row_names:
            table: Sequence[Sequence[Union[str, int, float]]] = [[
                row_name, *row
            ] for row_name, row in zip_longest(*(self.row_names, self.table),
                                               fillvalue='')]
            self.idx_col.add(0)
        else:
            table = self.table

        # format index columns with row_name format
        fmt_tab.extend([[
            self.compose(cell,
                         ('row-name' if cell_idx in self.idx_col else 'cell'))
            for cell_idx, cell in enumerate(row)
        ] for row in table])
        return fmt_tab

    def copy(self, parent):
        self.text = parent.text
        self.title = parent.title or self.title
        self.col_names = parent.col_names or self.col_names
        self.row_names = parent.row_names or self.row_names
        self.table = parent.table or self.table
        self.idx_col = parent.idx_col | self.idx_col

    def transpose_table(self):
        if self.table is None:
            return
        self._table = [col for col in zip_longest(*self.table, fillvalue='')]


class WayBarReturnType:
    """
    Waybar custom module return-type in JSON format.

    Parameters
    ----------
    text : Optional[str]
        Primary display text
    alt : Optional[str] = None
        alternate text used to decide icon, etc. by waybar
    tooltip : Optional[Union[WayBarToolTip, str]]
        Tooltip to display on hover.
    wclass : Optional[Union[List[str], str]]
        css class for styling

    percentage : Optional[float]
        numerical value used to decide icon, etc. by waybar
    """

    def __init__(self,
                 text: Optional[str] = None,
                 alt: Optional[str] = None,
                 tooltip: Optional[Union[WayBarToolTip, str]] = None,
                 wclass: Optional[Union[List[str], str]] = None,
                 percentage: Optional[float] = None):
        self.text = text
        """Displayed text."""

        self.alt = alt
        """Alternate string."""

        self.tooltip: WayBarToolTip = WayBarToolTip(tooltip)
        r"""Tooltip to display on hover, list is joined with '\n'"""

        self.class_ = wclass
        """Waybar style class"""

        self.percentage = percentage
        """Percentage for waybar-processing and classification"""

    def __str__(self) -> str:
        """dump to JSON string"""
        percentage = (None
                      if self.percentage is None else str(self.percentage))
        return json.dumps({
            'text': self.text,
            'alt': self.alt,
            'tooltip': str(self.tooltip),
            'class': self.class_,
            'percentage': percentage
        })


class KernelStats:
    """
    Kernel statistics monitor template.

    Handle that can monitor emit Kernel statistics in waybar JSON format.

    Parameters
    ----------
    tip_type : Optional[Sequence[str]]
        Initial tip type to decide format, etc.
    """

    tip_opts: Tuple[str, ...] = ('', )
    """Types of tooltips."""

    mon_name = ''
    """Name of monitor"""

    def __init__(self,
                 tip_type: Optional[Sequence[str]] = None,
                 interval: Optional[float] = None):
        self._config: Optional[ModConf] = None

        self.socket_commands: Dict[str, str] = {
            'next tip': 'next tip',
            'prev tip': 'prev tip',
            'refresh': 'refresh'
        }
        """Commands recognized by socket."""

        self.interval = (interval if
                         (interval is not None) else self.config.loop_interval)
        """
        Loop interval in seconds.
        If zero, call only once.

        May be configured using key 'loop-interval'.
        """

        self.cargo = WayBarReturnType()
        """Cargo to be loaded and sent as json to waybar."""

        if tip_type and all((tip not in self.tip_opts) for tip in tip_type):
            raise TipTypeError(tip_type)

        self._state_file: Optional[Path] = None

        self.register_state(tip_type)

    @property
    def config(self) -> ModConf:
        """Module specific configuration."""
        if self._config is None:
            self._config = ModConf(**CONFIG.get(self.mon_name, {}))
        return self._config

    @property
    def state_file(self) -> Path:
        """
        Path to file that stores the current state of tooltip type.

        State is stored as a single word in plain text.
        Perferred PREFIX location (in decreasing order):
        - ``$XDG_STATE_HOME`` (if exists)
        - ``$TMPDIR`` (if it exists)
        - '/tmp' (it it exists)
        - ./tmp/ (fallback)

        States file path is ``${PREFIX}/waybar/MON.dat``
        `MON` is :attr:`mon_name`.
        """
        if self._state_file is None:
            xdg_state = Path(
                os.getenv('XDG_RUNTIME_DIR') or os.getenv('TMPDIR') or '/tmp')
            if not xdg_state.is_dir():
                xdg_state = Path('./tmp/')
                xdg_state.mkdir(parents=True, exist_ok=True)
            self._state_file = xdg_state / (f'waybar/{self.mon_name}.dat')
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
        return self._state_file

    @property
    def sock_file(self) -> Path:
        """
        Path to file that opens a communication socket for the module.

        The value is the same as :attr:`state_file` with the extension '.sock'
        """
        return self.state_file.with_suffix('.sock')

    @property
    def tip_type(self) -> Sequence[str]:
        """
        Current state of tooltip.

        This is a read-only property, derived from :attr:`state_file`.
        This may be set at script initiation using command argument ``-t``;
        or the state may be pushed to the `next` value using ``-p``.
        """
        tips = []
        try:
            cache = self.state_file.read_text()
            tips = list(
                filter(lambda x: x in self.tip_opts,
                       [elt.strip().rstrip() for elt in cache.split('+')]))
            if not tips:
                raise TipTypeError(cache)  # this will be caught
        except (TipTypeError, FileNotFoundError):
            tips = list(
                filter(lambda x: x in self.tip_opts, [
                    elt.strip().rstrip()
                    for elt in self.config.tip_type.split('+')
                ]))
        return tips or self.tip_opts

    def __call__(self, interval: Optional[float] = None) -> int:
        """
        Loop periodically to emit JSON return object.

        When in loop, we listen to the socket :attr:`sock_file`.

        Parameters
        ----------
        interval: int
            Periodicity of loop. If not provided, use :attr:`interval`.
            If ``0``, call only once and return exit.

        Returns
        -------
        int
            Exit code 0 to pass to the OS.
        """
        # first call
        self.sense()
        print(self.cargo, flush=True)
        interval = interval if interval is not None else self.interval
        if not interval:
            return 0

        # loop
        self.sock_file.unlink(missing_ok=True)
        with socket.socket(socket.AF_UNIX,
                           socket.SOCK_STREAM) as sock:  # pragma: no cover
            sock.bind(str(self.sock_file))
            sock.listen(1)
            sock.settimeout(interval)
            while interval:
                # sleep(interval or self.interval)
                try:
                    conn, addr = sock.accept()
                    command = conn.recv(1024).decode()
                    if command == 'next tip':
                        self.next_tip(1)
                    elif command == 'prev tip':
                        self.next_tip(-1)
                except socket.timeout:
                    # socket timed out, next call
                    pass
                finally:
                    self.sense()

                    # print only if at least the configured lowest value
                    if ((self.cargo.percentage is None)
                            or (self.cargo.percentage >= self.config.lowest)):
                        print(self.cargo, flush=True)
                    else:
                        print('{"text": null}', flush=True)
        return 0

    def show_config(self) -> int:  # pragma: no cover
        """Print loaded configuration."""
        self.sense()
        print('\n'.join(
            (f'Configuration for {self.mon_name}:', str(self.config), '',
             'PANGO styles:', str(PANGO.styles), '', 'Sample Output:',
             str(self.cargo))))
        return 0

    def register_state(self, state: Optional[Sequence[str]] = None):
        """
        Register current state to :attr:`state_file`.

        Store value of current state for recurrnet reference and memory.

        Parameters
        ----------
        state : Optional[str]
            If supplied, this state is registered instead of current.
            This is useful for `pushing` the state.
        """
        self.state_file.write_text(' + '.join((state or self.tip_type)))

    def comm(self, data: str = 'refresh'):  # pragma: no cover
        """Client to communicate to the loop."""
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(str(self.sock_file))
            sock.sendall(data.encode())
        return 0

    def next_tip(self, direction: int = 1):
        """
        Use next tool-tip format.

        If current tooltip is simple, use it.
        If current tooltip is composite, use the first simple tooltip.

        Parameters
        ----------
        direction : int
            next tip is so many places way from current. (may be negative)
        """
        tip_type = self.tip_opts[(self.tip_opts.index(self.tip_type[0]) +
                                  direction) % len(self.tip_opts)]
        self.register_state([tip_type])

    def get_values(self):
        """Get values from system."""

    def set_percentage(self):
        """Set value for percentage."""

    def set_text(self):
        """
        Set display text.

        If this is ``None`` (default), the module segment is hidden.
        """

    def set_alt(self):
        """Set alternate text."""

    def set_tooltip(self):
        """Set value for tooltip."""

    def set_class(self):
        """Set value for class."""

    def sense(self):
        """Trigger sensors and calculations."""
        self.get_values()
        self.set_percentage()
        self.set_class()
        self.set_text()
        self.set_alt()
        self.set_tooltip()
