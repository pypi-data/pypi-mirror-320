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

from enum import StrEnum


class ContactName(StrEnum):
    """
    Enumeration representing various types of contact methods.

    This class defines different types of contact information that can be
    associated with a user or organization.  Each type is represented as
    an uppercase string value, following the vCard (Virtual Contact File)
    specification for electronic business cards.

    :note: The values of the enumeration members are explicitly defined
        as uppercase strings to comply with the vCard specification.
        `auto()` is not used to ensure the values remain consistent with
        this format.
    """
    # Represents an email contact method.
    EMAIL = 'EMAIL'

    # Represents a phone number contact method.
    PHONE = 'PHONE'

    # Represents a website contact method.
    WEBSITE = 'WEBSITE'
