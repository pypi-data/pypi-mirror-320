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

import logging
import re
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationInfo
from pydantic import field_validator

from thelittlehackers.constant.contact import ContactName
from thelittlehackers.constant.privacy import Visibility
from thelittlehackers.constant.regex import REGEX_PATTERN_EMAIL_ADDRESS
from thelittlehackers.constant.regex import REGEX_PATTERN_PHONE_NUMBER


REGEX_EMAIL_ADDRESS = re.compile(REGEX_PATTERN_EMAIL_ADDRESS)
REGEX_PHONE_NUMBER = re.compile(REGEX_PATTERN_PHONE_NUMBER)

CONTACT_NAME_REGEX_MAPPING = {
    ContactName.EMAIL: REGEX_EMAIL_ADDRESS,
    ContactName.PHONE: REGEX_PHONE_NUMBER,
}


class InvalidContactException(ValueError):
    """
    Indicate the value of a contact doesn't comply with the type of this
    contact.
    """


class Contact(BaseModel):
    """
    Represent a contact information, such as an e-mail address, a phone
    numbers, the Uniform Resource Locator (URL) of a website.
    """

    is_primary: bool = Field(
        default=False,
        description=(
            "Specify whether this contact information is the primary contact for "
            "this type of contact information."
        ),
        frozen=False
    )

    is_verified: bool = Field(
        default=False,
        description=(
            "Specify whether this contact information has been verified, i.e., it "
            "has been grabbed from a trusted Social Networking Service (SNS), or "
            "through a challenge/response process."
        ),
        frozen=False,
    )

    property_name: ContactName = Field(
        ...,
        description="The name (type) of this contact information:",
        frozen=True
    )

    property_parameters: Optional[str] = Field(
        ...,
        description=(
            "The property value of the contact information can be further qualified "
            "with a property parameter expression.  The property parameter "
            "expression is specified as either a single string or `name=value`,"
            "separated with comas."
        ),
        frozen=False
    )

    property_value: str = Field(
        ...,
        description=(
            "A string representation of the value associated to the contact "
            "information.  Each property must be unique for a given account, "
            "defined by both its name and value."
        ),
        frozen=True
    )

    visibility: Optional[Visibility] = Field(
        default=Visibility.PRIVATE,
        description="The visibility of this contact information to other users.",
        frozen=False
    )

    def __eq__(self, other):
        """
        Check whether this contact information to the one passed to this
        function.

        Two instances are equivalent when they are of the same type and they
        have the same value.


        :param other: an instance `Contact`.


        :return: `True` if this contact information corresponds to the
            contact information passed to this function; `False` otherwise.
        """
        return self.__property_name == other.__property_name \
            and self.__property_value == other.__property_value

    def __str__(self):
        """
        Return a nicely printable string representation of this contact
        information:

            [ name:string, value:string, is_primary:boolean, is_verified:boolean ]


        :return: a string of the array representation of this contact
            information.
        """
        return str([
            str(self.property_name),
            self.property_value,
            self.is_primary,
            self.is_verified
        ])

    @classmethod
    def assert_contact_value(
            cls,
            property_name: ContactName,
            property_value: str
    ) -> None:
        """
        Check that the contact value is valid.


        :param property_name: The contact information's type.

        :param property_value: The contact's value, such as for instance
            `+84.8272170781`, the formatted value for a telephone number
            property.


        :raise InvalidContactException: If the value of the contact doesn't
            comply with the type of this contact.

        :raise ValueError: If no regular expression mapping is defined for the
            given property name.  Please, contact the developers.
        """
        regex = CONTACT_NAME_REGEX_MAPPING.get(property_name)
        if regex is None:
            raise ValueError(
                f"No regex mapping found for contact type \"{property_name}\""
            )

        if not CONTACT_NAME_REGEX_MAPPING[property_name].match(property_value):
            raise cls.InvalidContactException(
                f"Invalid value \"{property_value}\" for contact type \"{property_name}\". "
                f"Expected format does not match."
            )

    @staticmethod
    def find_property_name(
            property_value: str
    ) -> ContactName:
        """
        Determine the contact type (property name) that corresponds to the
        provided contact value.


        :param property_value: A string representing a contact value (e.g.,
            an email address, phone number, or website URL).


        :return: The corresponding contact type (property name).


        :raise InvalidContactException: If no matching contact type is found
            for the provided property value, indicating that the value does
            not conform to any known contact formats.
        """
        for property_name, regex in CONTACT_NAME_REGEX_MAPPING.items():
            if regex.match(property_value):
                return property_name

        raise InvalidContactException(
            f"Invalid contact information: \"{property_value}\" does not match any "
            "recognized formats for contact types."
        )

    @classmethod
    def from_string(
            cls,
            property_value: str,
            is_primary: bool | None = None,
            is_verified: bool = False,
            visibility: Visibility | None = None
    ) -> Contact:
        """
        Create a ``Contact`` object based on a string representation of a
        contact value.

        This method attempts to determine the type of contact information (e.g.,
        email, phone, website) from the provided `property_value` string by
        matching it against predefined patterns.  If a match is found, it
        returns a `Contact` object initialized with the corresponding contact
        type and the specified attributes.


        :param property_value: A string representing the contact value (e.g.,
            an email address, phone number, or website URL).

        :param is_primary; Indicate whether this contact property is the
            primary method for contacting the entity. Only one primary contact
            is allowed per contact type (e.g., ``EMAIL``, ``PHONE``).
            Defaults to ``False``.

        :param is_verified; Indicate whether this contact information has been
            verified, either through a trusted Social Networking Service (SNS)
            or via a challenge/response process.  Defaults to ``False``.

        :param visibility: Optional; specifies the visibility of this contact
            information to other users. If not provided, defaults to
            `Visibility.PUBLIC`.


        :return: A `Contact` object representing the contact type and value,
            with the specified attributes.


        :raise InvalidContactException: If no matching contact type is found
            for the provided property value, indicating that the value does
            not conform to any known contact formats.
        """
        property_name = cls.find_property_name(property_value)

        return Contact(
            is_primary=is_primary,
            is_verified=is_verified,
            property_name=property_name,
            property_value=property_value,
            visibility=visibility
        )

    @field_validator('property_value', mode='before')
    @classmethod
    def validate_property_value(cls, value: str, info: ValidationInfo) -> str:
        """
        Validate the property value based on the property name, and convert it
        to lowercase.


        :param value: A string representation of the value associated to a
            contact information.

        :param info: An instance of `ValidationInfo` providing context during
            validation. This includes:

            - ``data``: A dictionary containing the values of the fields being
              validated in the model.  It allows access to other fields, such
              as ``property_name``, to perform cross-field validations.
             - Additional validation context and metadata.

        :return: The validated lowercase value.


        :raise ValueError: If the property_value does not match the
            expected format for the specified ``property_name`` field.
        """
        property_name = info.data.get('property_name')
        if property_name is None:
            raise ValueError("`property_name` must be set before validating `property_value`.")

        # Force to lowercase.
        lowercase_value = value.lower()
        if lowercase_value != value:
            logging.warning(
                f"The property value \"{value}\" contains uppercase letters.  Converting it "
                f"to lowercase: \"{lowercase_value}\"."
            )

        # Validate the `property_value` against the appropriate regex.
        cls.assert_contact_value(property_name, lowercase_value)

        return lowercase_value
