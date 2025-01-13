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

import unidecode


def normalize_names_codes_mapping(names_codes_mapping: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize the keys of a names-to-codes mapping.

    Key normalization makes it possible to support minor differences
    (basically lowercase or uppercase letters, and accents) of names
    when searching for the corresponding code.

    Examples:

    ```python
    >>> input_mapping = {"Français": "fr", "English": "en", "Español": "es"}
    >>> normalized_mapping = normalize_names_codes_mapping(input_mapping)
    >>> print(normalized_mapping)
    {"francais": "fr", "english": "en", "espanol": "es"}
    ```


    :param names_codes_mapping: A dictionary mapping names (strings) to
        their corresponding codes.  For example, language names and their
        ISO codes.


    :return: A new dictionary with normalized names (transliterated to
        ASCII lowercase string) as keys and the original codes as values.
    """
    normalized_names_codes_mapping = {
        normalize_key(key): value
        for key, value in names_codes_mapping.items()
    }

    return normalized_names_codes_mapping


def normalize_key(s: str) -> str:
    """
    Convert a string to lowercase ASCII.

    The function transliterates non-ASCII characters to their closest
    ASCII equivalents and converts the entire string to lowercase.


    :param s: A string to normalize.


    :return: The normalized string in lowercase ASCII format.
    """
    normalized_string = unidecode.unidecode(s.lower())
    return normalized_string
