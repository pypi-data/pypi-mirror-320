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

import datetime
import dateutil.parser
import re
import string
from enum import Enum
from typing import AnyStr
from typing import Callable
from typing import List
from typing import Type
from uuid import UUID

import normality

from thelittlehackers.constant import regex
from thelittlehackers.constant.data_type import DataType
from thelittlehackers.model.version import Version
from thelittlehackers.utils import any_utils
from thelittlehackers.utils import module_utils
from thelittlehackers.utils.any_utils import is_empty_or_none

REGEX_EMAIL_ADDRESS: re.Pattern[[AnyStr]] = re.compile(regex.REGEX_PATTERN_EMAIL_ADDRESS)
REGEX_IPV4: re.Pattern[AnyStr] = re.compile(regex.REGEX_PATTERN_IPV4)
REGEX_MAC_ADDRESS: re.Pattern[AnyStr] = re.compile(regex.REGEX_PATTERN_MAC_ADDRESS)


def is_empty(value: str) -> bool:
    """
    Checks if the specified value is empty.

    A value is considered empty if it is an empty string after stripping
    whitespace.


    :param value: The value to check for being empty.

    :return: ``True`` if the value is empty , ``False`` otherwise.


    :raise ValueError: if the input value is ``None``.
    """
    if value is None:
        raise ValueError("Input value cannot be None.")

    return len(value.strip()) == 0


def is_valid_email_address(value: str | None) -> bool:
    """
    Check if the provided string is a valid email address.


    :param value: A string to be checked as an email address.


    :return: ``True`` if the string is a valid email address, ``False``
        otherwise.
    """
    if is_empty_or_none(value):
        return False

    return REGEX_EMAIL_ADDRESS.match(value.strip().lower()) is not None


def string_to_boolean(
        value: bool | str | None,
        strict: bool = False,
        default_value: bool = False
) -> bool:
    """
    Convert a string representation of a boolean value to its
    corresponding boolean.

    This function interprets common string representations of boolean
    values (e.g., 'yes', 'true', '1') and returns the corresponding
    boolean.  If the ``strict`` parameter is set to ``True``, the function
    will raise a ``ValueError`` or if the string is not a recognized
    boolean representation.  Otherwise, it will return the ``default_value``
    or ``False`` if no valid representation is found.


    :param value: The input to be converted into a boolean.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        boolean strings.  If ``False``, the function returns ``None`` for
        invalid boolean strings.

    :param default_value: The boolean value to return if ``value`` is ``None``
        or an empty string.  Defaults to ``False``.


    :return: The boolean value corresponding to the string, or
        ``default_value`` if the string is not valid and ``strict`` is
        ``False``.


    :raise ValueError: If ``strict`` is ```True``` and `value` does not
        represent a valid boolean.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.lower()

    if value in ('yes', 'y', 'true', 't', '1'):
        return True

    if value in ('no', 'n', 'false', 'f', '0'):
        return False

    if strict:
        raise ValueError(f"The string \"{value}\" doesn't represent a boolean value")

    return default_value


def string_to_date(
        value: str | datetime.date | None = None,
        strict: bool = True
) -> datetime.date | None:
    """
    Convert a string representation of a date value to its corresponding
    date.


    :param value: The input to be converted into a date.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        date strings.  If ``False``, the function returns ``None`` for
        invalid date strings.


    :return: The date corresponding to the string.


    :raise OverflowError: Raised if the parsed date exceeds the largest
        valid C integer on your system.

    :raise ValueError: If ``strict`` is ```True``` and ``value`` does not
        represent a valid date or the string format is unknown.
    """
    try:
        date = None if any_utils.is_empty_or_none(value) \
            else value if isinstance(value, datetime.date) \
            else dateutil.parser.parse(value).date()
    except ValueError as error:
        if strict:
            raise error

    if date is None:
        if strict:
            f"The string \"{value}\" does not represent a date"

    return date


def string_to_decimal(
        value: str | float | None,
        strict: bool = True
) -> float | None:
    """
    Convert a string representation of a floating number value to its
    corresponding floating number.


    :param value: The input to be converted into an floating number.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        floating number strings.  If ``False``, the function returns
        ``None`` for invalid floating number strings.


    :return: The floating number value corresponding to the string.


    :raise ValueError: If ``strict`` is ```True``` and ``value`` does not
        represent a valid floating number.
    """
    try:
        decimal = None if any_utils.is_empty_or_none(value) \
            else value if isinstance(value, float) \
            else float(value)
    except ValueError as error:
        if strict:
            raise error

    if decimal is None:
        if strict:
            f"The string \"{value}\" does not represent a floating number"

    return decimal


def string_to_email_address(
        value: str | None,
        strict: bool = True
) -> str:
    """
    Convert a string to a normalized email address.

    This function attempts to convert the provided string into a valid,
    normalized email address (lowercased and stripped of surrounding
    whitespace).

    If the string is ``None``, empty, or not a valid email address, the
    function returns ``None`` unless ``strict`` mode is enabled.

    When ``strict`` is set to ``True``, the function raises a ``ValueError``
    if the input string is not a valid email address.


    :param value: The string to be converted to an email address.

    :param strict: A boolean flag that, if set to ``True``, raises a
        ``ValueError``.  If the string does not represent a valid email
        address.  Defaults to `True`.


    :return: The normalized email address as a string, or ``None`` if the
        input is invalid and ``strict`` is set to ``False``.


    :raises ValueError: If ``strict`` is ``True`` and the input string is
        not a valid email address.
    """
    email_address = None if is_empty_or_none(value) or not is_valid_email_address(value) \
        else value.strip().lower()

    if email_address is None and strict:
        raise ValueError(
            f"The string \"{value}\" does not represent an email address"
        )

    return email_address


def string_to_enumeration_member(
        value: str | Enum | None,
        enumeration: Type[Enum],
        strict: bool = True,
        default_value: Enum | None = None
) -> Enum | None:
    """
    Convert a string representation of an enumeration member to its
    corresponding enumeration member.


    :param value: The input value to convert.  It can be a string
        representing the name of an enumeration member, an existing
        enumeration member, or ``None``.

    :param enumeration: The enumeration class to which the value should
        belong.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        enumeration strings.  If ``False``, the function returns ``None``
        for invalid enumeration strings.

    :param default_value: The default enumeration member to return if
        ``value`` is ``None`` or an empty string.  Defaults to ``None``.


    :return: The corresponding enumeration member if conversion succeeds,
        or ``None`` if ``strict`` is ``False`` and conversion fails.


    :raise ValueError: If ``enumeration`` is not a subclass of ``Enum``.

    :raise ValueError: If ``value`` is a string that does not match any
        member of ``enumeration`` and ``strict`` is ``True``.
    """
    if not issubclass(enumeration, Enum):
        raise ValueError(
            "The argument \"enumeration\" must be a subclass of Enum.  Received "
            f"\"{enumeration.__name__}\" of class \"{enumeration.__class__.__name__}\" "
            f"instead."
        )

    try:
        enumeration_member = None if any_utils.is_empty_or_none(value) \
            else value if value in enumeration \
            else enumeration(value)
    except ValueError as error:
        if strict:
            raise error

    if enumeration_member is None:
        if default_value:
            enumeration_member = enumeration(default_value)
        elif strict:
            raise ValueError(
                f"The string \"{value}\" does not represent a member of the "
                f"enumeration \"{enumeration.__name__}\""
            )

    return enumeration_member


def string_to_integer(
        value: str | int | None,
        strict: bool = True
) -> int | None:
    """
    Convert a string representation of an integer value to its
    corresponding integer.


    :param value: The input to be converted into an integer.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        integer strings.  If ``False``, the function returns ``None`` for
        invalid integer strings.


    :return: The integer value corresponding to the string.


    :raise ValueError: If ``strict`` is ```True``` and ``value`` does not
        represent a valid integer.
    """
    try:
        integer = None if any_utils.is_empty_or_none(value) \
            else value if isinstance(value, int) \
            else int(value)
    except ValueError as error:
        if strict:
            raise error

    if integer is None:
        if strict:
            f"The string \"{value}\" does not represent an integer"

    return integer


def string_to_ipv4(
        value: str | None,
        strict: bool = True
) -> tuple[int, int, int, int] | None:
    """
    Convert a string representation of an IPv4 address into a tuple of
    four integers.

    Examples:
    >>> string_to_ipv4('192.168.1.1')
    (192, 168, 1, 1)

    >>> string_to_ipv4('256.168.1.1')
    ValueError: The IPv4 "256.168.1.1" has invalid byte(s)

    >>> string_to_ipv4(None)
    ValueError: The specified string "None" does not represent an IPv4

    >>> string_to_ipv4(None, strict=False)
    None


    :param value: The input to be converted into an IPv4 address.  It
        should be in the format `'X.X.X.X'`, where X is an integer between
        ``0`` and ``255``.   If ``value`` is ``None`` or an empty string,
         the function will return ``None`` unless ``strict`` is set to
         ``True``.

    :param strict: If ``True``, the function will raise a ``ValueError``
        if the string is ``None``, empty, or does not represent a valid
        IPv4 address.  If ``False``, the function will return ``None`` fpr
        such cases.


    :return: A tuple of four integers representing the IPv4 address, where
        each integer corresponds to one byte of the address (e.g.,
        ``(192, 168, 1, 1)``).  If ``value`` is ``None``, empty, or
        invalid (and ``strict`` is ``False``), the function returns ``None``.


    :raise ValueError: If the input string does not represent a valid IPv4
        address and ``strict`` is ``True``.  This includes cases where the
        string is ``None``, empty, or has invalid bytes (e.g., values not
        in the range ``0-255``).
    """
    match = None if any_utils.is_empty_or_none(value) else REGEX_IPV4.match(value)
    ipv4_address = match and match.group(0).split('.')

    if ipv4_address is None:
        if strict:
            raise ValueError(
                f"The string \"{value}\" does not represent a IPV4 address"
            )
    else:
        ipv4_address = tuple(
            int(component)
            for component in ipv4_address
        )

    return ipv4_address


def string_to_keywords(value: str, keyword_minimal_length: int = 1) -> List[str]:
    """
    Convert a string to a list of distinct keywords by removing
    punctuation, reducing whitespace, and converting accented Unicode
    characters to ASCII.

    This function cleanses a given string by:
    - Converting Unicode characters to their ASCII equivalents.
    - Removing all punctuation.
    - Reducing any multiple spaces to a single space.
    - Splitting the string into unique keywords and filtering by length.


    :param value: The input string to be processed into keywords.

    :param keyword_minimal_length: The minimum length a keyword must have
        to be included in the final list.


    :return: A list of unique keywords, stripped of punctuation,
        accentuated characters, and extra spaces, meeting the specified
        minimal length.
    """
    if is_empty_or_none(value):
        return []

    # Convert the string to ASCII lower characters.
    ascii_string = normality.normalize(value)

    # Replace any punctuation character with space.
    no_punctuation_string = ''.join([
        ' ' if c in string.punctuation else c
        for c in ascii_string
    ])

    # Remove any double space character.
    cleansed_string = re.sub(r'\s{2,}', ' ', no_punctuation_string)

    # Decompose the string into distinct keywords.
    distinct_keywords = set(cleansed_string.split(' '))

    # Filter out keywords of less than 2 characters.
    valid_keywords = [
        keywords
        for keywords in distinct_keywords
        if len(keywords) > keyword_minimal_length
    ]

    return valid_keywords


def string_to_locale(
        value: str | Locale | None,
        strict: bool = True
) -> Locale | None:
    """
    Convert a string representation of a locale to its corresponding
    ``Locale`` object.


    :param value: The input to be converted into a locale.  The input
        needs to be a ISO 639-3 alpha-3 code (or alpha-2 code), optionally
         followed by a dash character `-` and a ISO 3166-1 alpha-2 code.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, the input value must strictly comply
        with RFC 4646, otherwise a ``ValueError`` is raised.  If ``False``,
        the input value can be a Java-style locale (character `_` instead
        of `-`).


    :return: The ``Locale`` object corresponding to the string.


    :raise MalformedLocaleException: If ``locale`` does not represent a
        valid locale.
    """
    try:
        locale = None if any_utils.is_empty_or_none(value) \
            else value if isinstance(value, Locale) \
            else Locale.from_string(value, strict=strict)
    except Locale.MalformedLocaleException as exception:
        if strict:
            raise exception

    if locale is None:
        if strict:
            f"The string \"{value}\" does not represent a locale"

    return locale


def string_to_mac_address(
        value: str | None,
        strict: bool = True
) -> tuple[str, str, str, str, str, str] | None:
    """
    Convert a string representation of a Media Access Control (MAC)
    address into a tuple of hexadecimal strings.

    A MAC address is a unique identifier assigned to a network interface
    controller (NIC) for communications at the data link layer of a
    network segment. The standard IEEE 802 format for representing EUI-48
    addresses is six groups of two hexadecimal digits, separated by
    hyphens (e.g., ``01-23-45-67-89-AB``). Other common formats include:

    - Six groups separated by colons (e.g., ``01:23:45:67:89:AB``)
    - Three groups of four hexadecimal digits separated by dots (e.g.,
      ``0123.4567.89AB``)

    The function validates the input string against these formats and
    returns the corresponding hexadecimal components.


    :param value: A string representation of a MAC address.  If `None`,
        the function will behave according to the ``strict`` parameter.

    :param strict: If `True`, the function raises a ValueError when the
        input string does not match a valid MAC address format.  If
        ``False``, the function returns ``None`` for invalid inputs.


    :return: A tuple of six hexadecimal strings ``(hex1, hex2, hex3, hex4,
        hex5, hex6)`` representing the MAC address, each ranging from
        ``0x00`` to ``0xFF``.  Return ``None`` if the input is invalid and
        ``strict`` is set to ``False``.
    """
    match = None if any_utils.is_empty_or_none(value) else REGEX_MAC_ADDRESS.match(value)
    mac_address = match and match.group(0)

    if mac_address is None:
        if strict:
            raise ValueError(
                f"The string \"{value}\" does not represent a MAC address"
            )
    else:
        # Remove separator characters from the MAC address string
        # representation.
        mac_address_hexdigits = [
            c for c in mac_address if c in string.hexdigits
        ]

        # Split the string into pairs of characters.
        pairs = [
            mac_address_hexdigits[i:i + 2]
            for i in range(0, len(mac_address_hexdigits), 2)
        ]

        # Convert the list of pairs into a tuple.
        mac_address = tuple(pairs)

    return mac_address


def string_to_string(
        value: str | None
) -> str | None:
    """
    Return the input string if it is not empty or ``None``.


    :param value: A string.


    :return: The input string if it is non-empty and not ``None``;
        otherwise, ``None``.
    """
    return None if any_utils.is_empty_or_none(value) else value


def string_to_time(
        value: str | datetime.time | None,
        strict: bool = True
) -> datetime.time | None:
    """
    Convert a string representation of a time value into a `datetime.time`
    object.


    :param value: The input to be converted into a `datetime.time` object.
        This can be a string, a ``datetime.time`` object, or ``None``.
        A string must be given in the format `HH:MM` or `HH:MM:SS`, where:

        - ``HH``: Two-digit hour in 24-hour format (00-23).
        - ``MM``: Two-digit minute (00-59).
        - ``SS``: Two-digit second (00-59).

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        time strings.  If ``False``, the function returns ``None`` for
        invalid time strings.


    :return: A ``datetime.time`` object representing the time specified by
        the input string, or ``None`` if the input is ``None`` or an
        invalid string in non-strict mode.


    :raise ValueError: If ``strict`` is ```True``` and ``value`` does not
        represent a valid time in the expected format.
    """
    try:
        time = None if any_utils.is_empty_or_none(value) \
            else value if isinstance(value, datetime.time) \
            else datetime.datetime.strptime(value, '%H:%M:%S').time()
    except ValueError:
        try:
            return datetime.datetime.strptime(value, '%H:%M').time()
        except ValueError as error:
            if strict:
                raise error

    if time is None:
        if strict:
            f"The string \"{value}\" does not represent a time"

    return time


def string_to_timestamp(
        value: str | datetime.datetime | None,
        strict: bool = True
) -> datetime.datetime | None:
    """
    Convert a string representation of a date/time value into a
    ``datetime.datetime`` object.


    :param value: The input to be converted into a date/time.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        date/time strings.  If ``False``, the function returns ``None``
        for invalid date/time strings.


    :return: The date/time value corresponding to the string.


    :raise OverflowError: Raised if the parsed date exceeds the largest
        valid C integer on your system.

    :raise ValueError: If ``strict`` is ```True``` and ``value`` does not
        represent a valid date/time or the string format is unknown.
    """
    try:
        timestamp = None if any_utils.is_empty_or_none(value) \
            else value if isinstance(value, datetime.datetime) \
            else dateutil.parser.isoparse(value)
    except ValueError as error:
        if strict:
            raise error

    if timestamp is None:
        if strict:
            f"The string \"{value}\" does not represent a timestamp"

    return timestamp


def string_to_version(
        value: str | Version | None,
        strict: bool = True
) -> Version | None:
    """
    Convert a string representation of a version value to its
    corresponding version.


    :param value: The input to be converted into a version.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        version strings complying with Semantic Version 2.  If ``False``,
        the function returns ``None`` for invalid version strings.


    :return: The ``Version`` instance corresponding to the string.


    :raise ValueError: If ``strict`` is ```True``` and ``value`` does not
        represent a valid version or the string doesn't comply to Semantic
        Version 2.
    """
    try:
        version = None if any_utils.is_empty_or_none(value) \
            else value if isinstance(value, Version) \
            else Version.from_string(value)
    except ValueError as error:
        if strict:
            raise error

    if version is None:
        if strict:
            f"The string \"{value}\" does not represent a version"

    return version


def string_to_uuid(
        value: str | UUID | None,
        strict: bool = True
) -> UUID | None:
    """
    Convert a string representation of a UUID into a UUID object.

    This function attempts to parse the given string into a UUID object.
    If the string is not a valid UUID and strict mode is enabled, a
    ``ValueError`` is raised.  If strict mode is disabled, the function
    returns ``None`` when the string is not a valid UUID.


    :param value: The string to be converted into a UUID.  It should
        represent a valid UUID.  If the string is empty or ``None``, the
        function returns ``None``.

    :param strict: A boolean flag indicating whether to enforce strict
        validation.  If ``True``, a ``ValueError`` is raised for invalid
        UUID strings.  If ``False``, the function returns ``None`` for
        invalid UUID strings.


    :return: A UUID object corresponding to the given string, or ``None``
        if the string is invalid and strict mode is disabled.


    :raises ValueError: If ``strict`` is ``True`` and the string is not a
        valid UUID.
    """
    try:
        uuid = None if any_utils.is_empty_or_none(value) \
            else value if isinstance(value, UUID) \
            else UUID(value)
    except ValueError as error:
        if strict:
            raise error

    if uuid is None:
        if strict:
            f"The string \"{value}\" does not represent a UUID"

    return uuid


DATA_TYPE_CONVERTERS: {DataType, Callable} = {
    DataType.BOOLEAN: string_to_boolean,
    DataType.DATE: string_to_date,
    DataType.DECIMAL: string_to_decimal,
    # DataType.EMAIL_ADDRESS: __convert_to_email_address,
    DataType.ENUMERATION: string_to_enumeration_member,
    DataType.INTEGER: string_to_integer,
    DataType.IPV4: string_to_ipv4,
    # DataType.LIST: __convert_to_list,
    DataType.LOCALE: string_to_locale,
    DataType.MAC_ADDRESS: string_to_mac_address,
    DataType.STRING: string_to_string,
    DataType.TIME: string_to_time,
    DataType.TIMESTAMP: string_to_timestamp,
    DataType.UUID: string_to_uuid,
    DataType.VERSION: string_to_version,
}


# Dynamically load the class `Locale` to avoid circular import.
Locale = module_utils.load_class('thelittlehackers.model.locale.Locale')
