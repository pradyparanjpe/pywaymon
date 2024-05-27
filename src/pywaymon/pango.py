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
"""Pango markup interface."""

import re
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union

from xdgpspconf import BaseDisc

from pywaymon.errors import BadStyleClassError

CSS_RE = re.compile(
    r'\n\s*?((?:\S+\s*?)*?){\s*\n*((?:\s*\S+\s*:\s*\S+\s*;\s*\n*)*)}')
"""Pick Selector"""

ATTR_RE = re.compile(r"\s*(\S+)\s*:\s*(\S+)\s*;\s*\n*")
"""Pick style attributes"""

CLASS_RE = re.compile(r'(\.\S+|\*)')
"""Pick Classes"""


class PangoCssParser:
    """
    Minimal CSS Parser for Pango style sheet.

    Only following classes are recognised:
    - title
    - text (plain paragraph)
    - row-name (table)
    - col-name (table)
    - cell (table)

    Parameters
    ----------
    filenames : Optional[Union[Sequence[Path], Path]]
        Paths to css files. Optionally, a single file may be provided.
        If nothing is provided, style.css the configuration discovered
        directories are used.
    """
    classes = 'title', 'text', 'row-name', 'col-name', 'cell'

    def __init__(self,
                 filenames: Optional[Union[Sequence[Path], Path]] = None):
        self.styles: Dict[str, Dict[str, str]] = {
            class_: {}
            for class_ in self.classes
        }
        """Known, overwritten class styles."""

        filenames = filenames or [
            (conf_d / 'style.css') for conf_d in BaseDisc(
                'pywaymon', 'config', shipped=Path(__file__)).get_loc(
                    dom_start=False)
        ]
        if isinstance(filenames, Path):
            filenames = [filenames]

        for fn in filenames:
            if fn.exists():
                self.parse(fn)

    def parse(self, filename: Path):
        """
        Parse css file to extract and overwrite current style.

        Parameters
        ----------
        filename : Path
            path to style sheet
        """
        contents = '\n' + filename.read_text() + '\n'
        selectors = dict(CSS_RE.findall(contents))
        for select, conf in selectors.items():
            classes = map(lambda x: x.strip('.'), CLASS_RE.findall(select))
            attributes = dict(ATTR_RE.findall(conf))
            for class_ in classes:
                if class_ == '*':
                    for c in self.styles:
                        self.styles[c].update(attributes)
                elif class_ in self.styles:
                    self.styles[class_].update(attributes)

    def stylize(self,
                text: Any,
                class_: str = 'cell',
                custom: Optional[str] = None) -> str:
        """
        Stylize text using pango span tag.

        Stylize by placing tags at *{}* in `<span {}>text</span>`.

        Parameters
        ----------
        text : Any
            text to stylize, will be converted to string form.

        class_ : str
            Configured style class of text. If "custom", use custom parameter.

        custom : str
            A correctly formatted ('key=value') tag used as supplied.

        Raises
        ------
        BadStyleClassError
            style class is not recognized

        Returns
        -------
        str
            Text wrapped with <span key=value> </span>
        """

        _text = str(text)
        if class_ == 'custom':
            if not custom:
                return _text
            return f'<span {custom}>{_text}</span>'

        if class_ not in self.styles:
            raise BadStyleClassError(class_)

        tags = ' '.join((f'{p_tag}="{p_val}"'
                         for p_tag, p_val in self.styles[class_].items()
                         if (p_tag != 'clip')))

        if not tags:
            return _text
        return f'<span {tags}>{_text}</span>'
