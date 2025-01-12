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

import os
import re
from os import PathLike
from typing import ClassVar
from typing import Optional


import toml
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


class Version(BaseModel):
    """
    The software component version numbering is mostly inspired from
    Apache version numbering or similar other version numbering such as
    Semantic Versioning.  Version numbers are denoted using a standard
    tuple of integers: ``major.minor.patch``.

    A ``major`` version identifies the product stage of the project.  The
    basic intent is that ``major`` versions are incompatible, large-scale
    upgrades of the software component.  This enables a check of a client
    application against the latest version of the software component to
    ensure compatibility.  If there is a discrepancy between the two, the
    client application MUST be updated accordingly.

    A ``minor`` version is incremented when substantial new functionality
    or improvement are introduced; the ``major`` version number doesn't
    change.  A ``minor`` version retains backward compatibility with older
    minor versions.  It is NOT forward compatible as a previous ``minor``
    version doesn't include new functionality or improvement that has been
    introduced in this newer ``minor`` version.

    A ``patch`` version is incremented when bugs were fixed or
    implementation details were refactored.  The ``major`` and ``minor``
    version don't change.  A ``patch`` version is backward and forward
    compatible with older and newer patches of the same major and minor
    version.

    References:

    * Apache Portable Runtime (APR)'s Version Numbering
      (http://apr.apache.org/versioning.html)
    * Semantic Versioning (http://semver.org/)
    * PEP 386 - Changing the version comparison module in Distutils
      (http://www.python.org/dev/peps/pep-0386/)
    """
    major: int = Field(..., ge=0, description="Major version number.")
    minor: int = Field(0, ge=0, description="Minor version number.")
    patch: int = Field(0, ge=0, description="Patch version number.")

    prerelease: Optional[str] = Field(
        None,
        description="Pre-release version."
                    ""
                    "A pre-release version indicates that the version is unstable and might "
                    "not satisfy the intended compatibility requirements as denoted by its "
                    "associated normal version."
    )

    build_metadata: Optional[str] = Field(
        None,
        description="Build metadata."
                    ""
                    "Build metadata is intended to track build maturity when preparing an "
                    "application for a public release of any kind, including pre-releases."
                    ""
                    "It can sometimes be helpful to include information such as:"
                    ""
                    "- The exact git hash of the commit used to produce the current build."
                    ""
                    "- The release channel of the build.  For example, is this build a very "
                    "experimental and potentially broken \"nightly\" release, a semi-stable "
                    "\"beta\" release containing a few new experimental features, or a "
                    "robust and well-tested \"stable\" release?"
                    ""
                    "- Whether the project as a whole is alpha-level quality (the entire "
                    "project is pretty new and experimental)."
    )

    # Name of the file in which the version of an application is commonly
    # written.
    DEFAULT_VERSION_FILE_NAME: ClassVar[str] = 'VERSION'

    # Regular expression that matches the string representation of a version
    # denoted using a standard tuple of integers ``major.minor.patch``.
    REGEX_PATTERN_SEMANTIC_VERSION: ClassVar[re.Pattern] = re.compile(
        r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
        r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
        r'(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    )

    model_config = ConfigDict(exclude_none=True)

    @field_validator('major', 'minor', 'patch')
    @classmethod
    def non_negative(cls, value: int):
        if value < 0:
            raise ValueError("Version components must be non-negative.")
        return value


    @classmethod
    def from_file(cls, path: PathLike, file_name: str | None = None) -> Version:
        """
        Return a version written in a file.


        :param path: The absolute path of the version file.

        :param file_name: The name of the file where the version is written in.
            It defaults to {@link Version.DEFAULT_VERSION_FILE_NAME}.


        :return: An object {@link Version}.
        """
        version_file_path = os.path.join(path, file_name or cls.DEFAULT_VERSION_FILE_NAME)
        with open(version_file_path, mode='rt', encoding='utf-8') as fd:
            version_str = fd.read().strip()
        return cls.from_string(version_str)


    @classmethod
    def from_pyproject(
            cls,
            project_root_path: PathLike,
            strict: bool = True
    ) -> Version | None:
        """
        Retrieve the version of the project from the ``pyproject.toml`` file.

        This method opens the 'pyproject.toml' file  and extract the version
        specified under the ``[tool.poetry.version]`` key.  If successful, it
        returns a ``Version`` object initialized with the version string.


        :param project_root_path: The root path of the Python project.

        :param strict: If ``True``, the method raises an exception if the
            version information is unavailable or cannot be parsed.


        :return: A ``Version`` instance representing the version of the
            project, or `None` if the version information is unavailable or
            cannot be parsed and ``strict`` is set to ``False``.


        :raise FileNotFoundError: If the ``pyproject.toml`` file is not found
            and ``strict`` is ``True``.

        :raise KeyError: If the ``version`` key is missing in the
            ``pyproject.toml`` file and ``strict`` is ``True``.
        """
        pyproject_path_file_name = os.path.join(project_root_path, 'pyproject.toml')
        try:
            with open(pyproject_path_file_name, mode='rt') as fd:
                data = toml.load(fd)
            version_str = data['tool']['poetry']['version']
            return cls.from_string(version_str)
        except (FileNotFoundError, KeyError) as exception:
            if strict:
                raise exception

        return None

    @classmethod
    def from_string(cls, value: str) -> Version:
        """
        Return the version corresponding to the specified string.


        :param value: A string representing a version.


        :return: The version corresponding to the string, or ``None`` if the
            argument ``s`` is null.
        """
        match = cls.REGEX_PATTERN_SEMANTIC_VERSION.match(value)
        if not match:
            raise ValueError(f"Invalid version string: {value}")

        major, minor, patch = int(match.group('major')), int(match.group('minor')), int(match.group('patch'))
        prerelease = match.group('prerelease')
        build_metadata = match.group('buildmetadata')
        return cls(major=major, minor=minor, patch=patch, prerelease=prerelease, build_metadata=build_metadata)

    def __eq__(self, other: Version) -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __gt__(self, other: Version) -> bool:
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __lt__(self, other: Version) -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __str__(self) -> str:
        version_str = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version_str += f"-{self.prerelease}"
        if self.build_metadata:
            version_str += f"+{self.build_metadata}"
        return version_str
#

