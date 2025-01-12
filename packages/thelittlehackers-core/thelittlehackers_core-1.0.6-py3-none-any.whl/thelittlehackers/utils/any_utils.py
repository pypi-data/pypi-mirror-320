# MIT License
#
# Copyright (C) 2019 The Little Hackers.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import annotations

from typing import Any
from typing import Sized
from typing import SupportsFloat
from typing import SupportsInt
from uuid import UUID


def is_empty_or_none(value: Any) -> bool:
    """
    Checks if the specified value is empty or ``None``.

    A value is considered empty or ``None`` if it is:
    - `None`
    - An empty string (after stripping whitespace)
    - An empty collection (e.g., ``list``, ``tuple``, ``set``, etc.)
    - An object that evaluates to ``False`` (e.g., empty lists, empty
      dictionaries, etc.)

    Numeric types (integers, floats) and boolean values are never
    considered empty.


    :param value: The value to check for being empty or ``None``.  This
        can be of any type.

    :return: ``True`` if the value is empty or ``None``, ``False`` otherwise.
    """
    if value is None:
        return True
    elif isinstance(value, (bool, float, int)):
        return False
    elif isinstance(value, str):
        return len(value.strip()) == 0
    elif isinstance(value, Sized):
        return len(value) == 0
    else:
        return not value


def is_integer(value: int | str | SupportsInt | None) -> bool:
    """
    Check if the provided input represents an integer or can be converted
    to one.

    This function determines whether the input is an integer, a string
    that represents an integer, or any type that implements the ``__int__``
    method (via the `SupportsInt` protocol).  If the input is ``None`` or
    cannot be converted to an integer, the function returns ``False``.


    :param value: The input to check, which may be an integer or a value
        that can be converted to an integer.


    :return: ``True`` if the input is an integer or can be converted to an
        integer; ``False`` otherwise.
    """
    if value is None:
        return False

    if isinstance(value, (int, SupportsInt)):
        return True

    try:
        int(value)
        return True
    except (TypeError, ValueError):
        return False


def is_numeric(value: float | str | SupportsFloat | None) -> bool:
    """
    Check if the provided input represents a numeric value or can be
    converted to one.

    This function determines whether the input is a floating point number,
    a string that represents a numeric value, or any type that implements
    the ``__float__`` method (via the `SupportsFloat` protocol).  If the
    input is ``None`` or cannot be converted to a floating point number,
    the function returns ``False``.

    :param value: The input to check, which can be a float, a string
        representation of a numeric value, a type that supports conversion to
        a floating point number, or ``None``.

    :return: ``True`` if the input is a floating point number or can be
        converted to a numeric value; ``False`` otherwise.
    """
    if value is None:
        return False

    if isinstance(value, float):
        return True
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def is_uuid(value: str | UUID | None) -> bool:
    """
    Check if the provided input represents a Universally Unique Identifier
    (UUID).


    :param value: The input to check, which can be a string representation
        of a UUID, a UUID object, or ``None``.


    :return: ``True`` if the input is a UUID object or can be converted to
        a UUID; ``False`` otherwise.
    """
    if value is None:
        return False

    if isinstance(value, UUID):
        return True

    try:
        return UUID(value) is not None
    except (TypeError, ValueError):
        return False
