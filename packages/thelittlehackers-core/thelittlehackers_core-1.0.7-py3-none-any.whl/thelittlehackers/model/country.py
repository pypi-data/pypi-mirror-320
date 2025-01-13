# MIT License
#
# Copyright (C) 2024 The Little Hackers.  All rights reserved.
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

from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from thelittlehackers.constant.locale import ISO_3166_1_ALPHA_2_CODES
from thelittlehackers.utils import string_utils


class InvalidCountryCode(Exception):
    """
    Indicate that a string doesn't match a valid country code.
    """


class Country(BaseModel):
    """
    Represent a country that corresponds to a tag respecting ISO 3166.

    A country is expressed by a ISO 3166-1 alpha-2 code.  For example, "US"
    represents the United States of America.
    """
    country_code: Optional[str] = Field(
        None,
        description="An ISO 3166-1 alpha-2 code.",
        frozen=True
    )

    @classmethod
    def assert_country_code(cls, code: str, strict: bool = True) -> None:
        """
        Assert that a country code is valid.


        :param code: A country code.

        :param strict: Indicate whether the comparison of the country code
            string is case-sensitive or not.


        :raise InvalidCountryCodeException: If the country code passed to this
            function doesn't match a valid language code.
        """
        if not cls.is_country_code(code, strict=strict):
            raise InvalidCountryCode(f"Invalid country code \"{code}\"")

    def __eq__(self, other: object) -> bool:
        """
        Indicate whether this locale is the same as the other locale.

        Two locale objects are the same when they correspond to the same
        language and the same country (unless no country is defined for both
        locales).


        :param other: The other locale to compare.


        :return: Indicate whether this locale is the identical to the other
            locale.
        """
        if not isinstance(other, Country):
            return False

        return self.__country_code == other.country_code

    def __hash__(self) -> int:
        if not hasattr(self, '__hash'):
            self.__hash = sum([
                (ord(c) - ord('a') if ord(c) >= ord('a') else ord(c) - ord('A')) * 52**i
                for i, c in enumerate(self.__country_code)
            ])

        return self.__hash

    def __repr__(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()

    @staticmethod
    def from_string(country_code: str | None, strict: bool = True) -> Country | None:
        """
        Return an object `Country` corresponding to the string representation
        of a country.


        :param country_code: A ISO 3166-1 alpha-2 code.


        :param strict: Indicate whether the string representation of a country
            MUST be given in uppercase.


        :return: An object ``Country`` or ``None`` if the argument ``country`` is
            ``None``.
        """
        if not country_code:
            return None

        return Country(country_code=country_code)

    @classmethod
    def is_country_code(cls, code: str, strict: bool = True) -> bool:
        return cls.is_iso_3166_1_alpha_2(code, strict=strict)

    @staticmethod
    def is_iso_3166_1_alpha_2(code: str, strict: bool = True) -> bool:
        return (code if strict else code.upper()) in ISO_3166_1_ALPHA_2_CODES

    def to_string(self) -> str:
        """
        Return a string representation of this object `Country`.


        :return: A string representation of a country, i.e., a ISO 3166-1
            alpha-2 code.
        """
        return self.__country_code

    @field_validator('country_code', mode='before')
    @classmethod
    def validate_country_code(cls, value: str | None) -> str | None:
        """
        Validate the given country code as a valid ISO 3166-1 alpha-2 code.


        :param value: An ISO 3166-1 alpha-2 country code (e.g., 'US' for the
            United States) or `None`.


        :return: An ISO 3166-1 alpha-2 code or `None`.


        :raise ValueError: If the given country code not `None` and is invalid.
        """
        if string_utils.is_empty_or_none(value):
            return None

        value = value.upper()
        cls.assert_country_code(value, strict=True)

        return value