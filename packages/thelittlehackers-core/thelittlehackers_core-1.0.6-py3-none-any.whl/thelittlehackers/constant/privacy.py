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
from enum import auto


class Visibility(StrEnum):
    """
    Enumeration representing the visibility levels for a resource.

    This class defines the various access control levels that can be
    assigned to resources, specifying who can view, access, or interact
    with the resource.
    """
    # The resource is accessible only to family members.
    FAMILY = auto()

    # The resource is accessible only to friends.
    FRIEND = auto()

    # The resource is restricted to a specific individual or a select
    # group of individuals.  Only the owner or the people explicitly
    # granted access can view, access, or interact with the resource.
    PRIVATE = auto()

    # The resource is accessible to anyone, regardless of whether they are
    # logged in or part of a specific group.  In a public setting, anyone
    # can view, access, or interact with the resource without restrictions.
    PUBLIC = auto()

    # The resources that are accessible only to members of a specific
    # group or team within an organization or project.  All team members
    # have access, and they can view, edit, or manage the resource
    # depending on their permissions.
    TEAM = auto()
