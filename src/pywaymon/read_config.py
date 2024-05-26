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

from pathlib import Path
from typing import Any, Dict, Optional, Union

from xdgpspconf import ConfDisc

_ATOMIC = (int, float, str)

_CONFTYPE = (None, int, float, str, dict, list)


def walk_update(
    base: Optional[Union[int, float, str, dict, list]] = None,
    override: Optional[Union[int, float, str, dict, list]] = None
) -> Optional[Union[int, float, str, dict, list]]:
    """
    Recursively update each iterable element.

    Walk down the data till we reach atomic objects: [str, int, float, None]
    and return updating each iterable.

    Parameters
    ----------
    base : CONFTYPE
        Make changes in this basic object.
    override : CONFTYPE
        Override with these changes. Specifically, to override
        as ``None``, set to the special string "___NONE___".

    Returns
    -------
    CONFTYPE
        Composed Object
    """
    # Trivial case: No conflict
    if override is None:
        return base

    if isinstance(base, _ATOMIC) or base is None:
        return override

    if override == '___NONE___':
        return None

    # Base is composite
    if isinstance(base, dict):
        if isinstance(override, dict):
            # both are dicts, next stack
            for o_key, o_val in override.items():
                # update base
                base[o_key] = walk_update(base.get(o_key), o_val)
            return base
        return override

    assert isinstance(base, list)
    if isinstance(override, list):
        return base + override
    return override


def read_config() -> Dict[str, Any]:
    """
    Discover configurations and overlay them appropriately.

    This is not the same as 'Flatten', which updates the global dict.
    Here, we want to walk down each object or list and update it.
    """
    # TODO: Merge upstream into xdgpspconf
    all_configs = ConfDisc('pywaymon',
                           shipped=Path(__file__)).read_config(dom_start=False)
    merged: Optional[dict] = None
    for conf in all_configs.values():
        merged = walk_update(merged, conf)  # type: ignore [assignment]
    return merged or {}
